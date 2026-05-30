import json
import os
import re
from datetime import datetime
from urllib.parse import urlparse

from common.log import logger


MAX_SOURCES = 10
MAX_FETCHED_SOURCES = 5
MAX_CONTENT_CHARS = 3500


def build_research_plan(topic: str, options: dict = None) -> dict:
    topic = str(topic or "").strip()
    options = dict(options or {})
    depth = options.get("depth", "standard")
    queries = [
        topic,
        f"{topic} 行业现状 市场规模",
        f"{topic} 典型案例 实践",
        f"{topic} 技术路线 架构",
        f"{topic} 风险 挑战 趋势",
    ]
    if depth == "fast":
        queries = queries[:3]
    elif depth == "deep":
        queries.extend([
            f"{topic} 竞品 对比 分析",
            f"{topic} 政策 合规 数据",
            f"{topic} 未来趋势 投资 机会",
        ])
    sections = [
        "摘要",
        "核心结论",
        "背景与现状",
        "关键技术或业务逻辑",
        "典型案例与可借鉴经验",
        "机会、风险与挑战",
        "行动建议",
        "参考来源",
    ]
    return {
        "topic": topic,
        "options": options,
        "created_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "queries": queries,
        "sections": sections,
        "source_policy": "优先使用可访问网页的标题、摘要、发布时间和正文摘录；重要结论应尽量由来源支持。",
    }


def collect_research(topic: str, job: dict, options: dict = None) -> dict:
    options = dict(options or job.get("options") or {})
    max_sources = _int_option(options, "max_sources", MAX_SOURCES, 1, 20)
    max_fetched = _int_option(options, "max_fetched_sources", MAX_FETCHED_SOURCES, 0, max_sources)
    content_chars = _int_option(options, "content_chars", MAX_CONTENT_CHARS, 1000, 8000)

    plan = build_research_plan(topic, options)
    _write_json(job.get("plan_path", ""), plan)

    search_results = _run_searches(plan["queries"])
    sources = _dedupe_sources(search_results)
    fetched = _fetch_source_contents(sources[:max_fetched], content_chars)

    by_url = {item.get("url"): item for item in fetched if item.get("url")}
    enriched = []
    for source in sources[:max_sources]:
        item = dict(source)
        if source.get("url") in by_url:
            item.update(by_url[source["url"]])
        enriched.append(item)

    source_status, source_label, source_notice = _source_summary(enriched, search_results)
    pack = {
        "topic": topic,
        "plan": plan,
        "options": options,
        "source_count": len(enriched),
        "source_status": source_status,
        "source_label": source_label,
        "source_notice": source_notice,
        "sources": enriched,
        "warnings": [],
    }
    if not search_results:
        if _search_backend_configured():
            pack["warnings"].append("外部检索已配置，但本次未获取到可用搜索结果；报告已标注资料限制。")
        else:
            pack["warnings"].append("外部检索未配置；报告将基于模型已有知识生成 V4 草稿，并标注资料限制。")
    _write_json(job.get("sources_path", ""), pack)
    return pack


def format_research_for_prompt(research_pack: dict) -> str:
    sources = research_pack.get("sources", []) or []
    if not sources:
        return "暂无外部来源。请明确标注资料限制，并基于已有知识形成可审阅草稿。"

    blocks = []
    for idx, src in enumerate(sources, 1):
        title = src.get("title", "") or "(无标题)"
        url = src.get("url", "")
        date = src.get("datePublished", "") or src.get("date", "")
        snippet = src.get("snippet", "") or src.get("summary", "")
        content = src.get("content_excerpt", "")
        block = [
            f"[{idx}] {title}",
            f"URL: {url}",
        ]
        if date:
            block.append(f"日期: {date}")
        if snippet:
            block.append(f"摘要: {snippet}")
        if content:
            block.append(f"正文摘录: {content}")
        blocks.append("\n".join(block))
    return "\n\n".join(blocks)


def references_markdown(research_pack: dict) -> str:
    sources = research_pack.get("sources", []) or []
    if not sources:
        notice = research_pack.get("source_notice") or "暂无可用外部来源。本报告已在正文中标注资料限制。"
        return f"## 参考来源\n\n{notice}\n"
    lines = ["## 参考来源", ""]
    for idx, src in enumerate(sources, 1):
        title = (src.get("title") or "无标题").strip()
        url = (src.get("url") or "").strip()
        site = (src.get("siteName") or _domain(url)).strip()
        date = (src.get("datePublished") or "").strip()
        meta = "，".join(part for part in [site, date] if part)
        suffix = f"（{meta}）" if meta else ""
        if url:
            lines.append(f"{idx}. [{title}]({url}){suffix}")
        else:
            lines.append(f"{idx}. {title}{suffix}")
    lines.append("")
    return "\n".join(lines)


def _run_searches(queries: list) -> list:
    try:
        from agent.tools.web_search.web_search import WebSearch
    except Exception as e:
        logger.warning(f"[Reports] WebSearch unavailable: {e}")
        return []

    tool = WebSearch()
    results = []
    for query in queries:
        try:
            ret = tool.execute({"query": query, "count": 5, "freshness": "noLimit", "summary": True})
            if ret.status != "success":
                logger.info(f"[Reports] Search skipped for '{query}': {ret.result}")
                continue
            data = ret.result if isinstance(ret.result, dict) else {}
            for item in data.get("results", []) or []:
                if item.get("url"):
                    item = dict(item)
                    item["query"] = query
                    results.append(item)
        except Exception as e:
            logger.warning(f"[Reports] Search failed for '{query}': {e}")
    return results


def _search_backend_configured() -> bool:
    return bool(
        os.environ.get("BOCHA_API_KEY")
        or os.environ.get("LINKAI_API_KEY")
    )


def _source_summary(sources: list, search_results: list) -> tuple:
    count = len(sources or [])
    if count > 0:
        return "verified", f"{count} 个外部来源", f"本报告整理了 {count} 个外部来源，并在正文或参考来源中标注。"
    if not _search_backend_configured():
        return (
            "search_not_configured",
            "外部来源待补充",
            "当前未配置外部检索服务，未能自动附加可验证网页来源；报告已标注资料限制，建议配置 Bocha 或 LinkAI 搜索后重新生成。",
        )
    if not search_results:
        return (
            "search_empty",
            "外部来源待补充",
            "本次外部检索未返回可用来源；报告已标注资料限制，建议补充关键词或重新生成。",
        )
    return (
        "source_unavailable",
        "外部来源待补充",
        "本次检索结果未能整理为可用来源；报告已标注资料限制。",
    )


def _fetch_source_contents(sources: list, content_chars: int = MAX_CONTENT_CHARS) -> list:
    try:
        from agent.tools.web_fetch.web_fetch import WebFetch
    except Exception as e:
        logger.warning(f"[Reports] WebFetch unavailable: {e}")
        return []

    tool = WebFetch()
    fetched = []
    for source in sources:
        url = source.get("url", "")
        if not url:
            continue
        try:
            ret = tool.execute({"url": url})
            if ret.status != "success":
                continue
            text = str(ret.result or "")
            title = _extract_title(text) or source.get("title", "")
            content = _extract_content(text)
            fetched.append({
                "url": url,
                "title": title,
                "content_excerpt": content[:content_chars],
                "fetched": True,
            })
        except Exception as e:
            logger.debug(f"[Reports] Fetch failed for {url}: {e}")
    return fetched


def _dedupe_sources(items: list) -> list:
    seen = set()
    deduped = []
    for item in items:
        url = _canonical_url(item.get("url", ""))
        if not url or url in seen:
            continue
        seen.add(url)
        copied = dict(item)
        copied["url"] = url
        deduped.append(copied)
    return deduped


def _canonical_url(url: str) -> str:
    url = str(url or "").strip()
    if not url:
        return ""
    return url.split("#", 1)[0]


def _extract_title(text: str) -> str:
    m = re.search(r"^Title:\s*(.+)$", text, flags=re.M)
    return m.group(1).strip() if m else ""


def _extract_content(text: str) -> str:
    if "Content:\n" in text:
        text = text.split("Content:\n", 1)[1]
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


def _write_json(path: str, data: dict):
    if not path:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _int_option(options: dict, key: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(options.get(key, default))
    except Exception:
        value = default
    return max(minimum, min(maximum, value))
