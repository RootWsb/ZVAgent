import os
import re
import threading

from bridge.context import Context, ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from common.user_identity import context_user_key
from config import conf

from .renderer import render_html, render_pdf
from .research import collect_research, format_research_for_prompt, references_markdown
from .store import ReportStore


REPORT_COMMANDS = ("/报告", "/report")
REPORT_STATUS_COMMANDS = ("/报告状态", "/report_status", "/report-status")
REPORT_LIST_COMMANDS = ("/报告列表", "/report_list", "/report-list")
REPORT_HELP_COMMANDS = ("/报告帮助", "/report_help", "/report-help")


DEPTH_PRESETS = {
    "fast": {
        "label": "快速",
        "target_words": 1800,
        "max_sources": 5,
        "max_fetched_sources": 3,
        "content_chars": 2500,
    },
    "standard": {
        "label": "标准",
        "target_words": 3000,
        "max_sources": 10,
        "max_fetched_sources": 5,
        "content_chars": 3500,
    },
    "deep": {
        "label": "深度",
        "target_words": 5000,
        "max_sources": 15,
        "max_fetched_sources": 8,
        "content_chars": 5000,
    },
}


def parse_report_command(text: str) -> dict:
    raw = str(text or "").strip()
    lowered = raw.lower()
    for prefix in REPORT_HELP_COMMANDS:
        if lowered.startswith(prefix.lower()):
            return {"action": "help"}
    for prefix in REPORT_LIST_COMMANDS:
        if lowered.startswith(prefix.lower()):
            return {"action": "list"}
    for prefix in REPORT_STATUS_COMMANDS:
        if lowered.startswith(prefix.lower()):
            job_id = raw[len(prefix):].strip()
            return {"action": "status", "job_id": job_id}
    for prefix in REPORT_COMMANDS:
        if lowered.startswith(prefix.lower()):
            topic_text = raw[len(prefix):].strip(" ：:\n\t")
            topic, options = _parse_report_options(topic_text)
            return {"action": "create", "topic": topic, "options": options}
    if raw.startswith("生成报告"):
        topic_text = raw[len("生成报告"):].strip(" ：:\n\t")
        topic, options = _parse_report_options(topic_text)
        return {"action": "create", "topic": topic, "options": options}
    return {}


def handle_report_command(context, channel) -> bool:
    parsed = parse_report_command(context.content)
    if not parsed:
        return False

    if parsed["action"] == "status":
        _send(channel, context, _format_status(context, parsed.get("job_id", "")))
        return True

    if parsed["action"] == "list":
        _send(channel, context, _format_user_report_list(context))
        return True

    if parsed["action"] == "help":
        _send(channel, context, _report_help_text())
        return True

    topic = parsed.get("topic", "").strip()
    if not topic:
        _send(channel, context, _report_help_text())
        return True

    options = parsed.get("options") or _default_options("standard")
    store = ReportStore()
    user_id = context_user_key(context)
    existing = store.find_recent_similar_job(
        user_id=user_id,
        topic=topic,
        options=options,
        within_seconds=int(conf().get("report_duplicate_window_seconds", 120) or 120),
    )
    if existing:
        _send(
            channel,
            context,
            f"已存在相同报告任务：{existing['job_id']}\n主题：{topic}\n我不会重复创建，继续等待原任务完成即可。\n\n查询进度：/报告状态 {existing['job_id']}",
        )
        return True

    job = store.create_job(
        user_id=user_id,
        channel_type=context.get("channel_type", ""),
        topic=topic,
        display_name=context.get("display_name", ""),
        options=options,
    )
    option_line = f"模式：{options.get('label', '标准')} / 约 {options.get('target_words', 3000)} 字 / 最多 {options.get('max_sources', 10)} 个来源"
    _send(
        channel,
        context,
        f"已创建报告任务：{job['job_id']}\n主题：{topic}\n{option_line}\n我会在后台生成 PDF，完成后自动把下载链接发给你。\n\n查询进度：/报告状态 {job['job_id']}",
    )
    thread = threading.Thread(
        target=_run_report_job,
        args=(job["job_id"], context, channel),
        daemon=True,
        name=f"report-{job['job_id']}",
    )
    thread.start()
    return True


def _format_status(context, job_id: str) -> str:
    job_id = str(job_id or "").strip()
    if not job_id:
        return "请发送：/报告状态 任务编号"
    store = ReportStore()
    job = store.find_user_job(context_user_key(context), job_id)
    if not job:
        return f"没有找到你的报告任务：{job_id}"
    status_map = {
        "queued": "排队中",
        "running": "生成中",
        "researching": "调研中",
        "writing": "写作中",
        "rendering": "排版中",
        "done": "已完成",
        "failed": "失败",
    }
    status = status_map.get(job.get("status"), job.get("status", "未知"))
    if job.get("status") == "done":
        source_line = _format_job_source_line(job)
        return f"报告任务 {job_id} 已完成。\n{source_line}\n下载链接：{_download_url(job)}"
    if job.get("status") == "failed":
        return f"报告任务 {job_id} 生成失败：{job.get('error', '') or '未知错误'}"
    progress = job.get("progress", "")
    percent = job.get("progress_percent", "")
    percent_line = f"（{percent}%）" if percent != "" else ""
    progress_line = f"\n进度：{progress}{percent_line}" if progress else ""
    return f"报告任务 {job_id} 当前状态：{status}{progress_line}\n主题：{job.get('topic', '')}"


def _format_user_report_list(context) -> str:
    store = ReportStore()
    result = store.list_jobs(page=1, page_size=8, user_id=context_user_key(context))
    items = result.get("items", [])
    if not items:
        return "你还没有报告任务。发送：/报告 主题，即可创建一份 PDF 报告。"
    status_map = {
        "queued": "排队中",
        "researching": "调研中",
        "writing": "写作中",
        "rendering": "排版中",
        "done": "已完成",
        "failed": "失败",
    }
    lines = ["最近报告任务："]
    for item in items:
        status = status_map.get(item.get("status"), item.get("status", "未知"))
        percent = item.get("progress_percent", "")
        percent_text = f" {percent}%" if percent != "" else ""
        lines.append(f"- {item.get('job_id')}｜{status}{percent_text}｜{item.get('topic', '')}")
    lines.append("\n查询单个任务：/报告状态 任务编号")
    return "\n".join(lines)


def _run_report_job(job_id: str, source_context, channel):
    store = ReportStore()
    job = store.get_job(job_id)
    if not job:
        return
    try:
        options = dict(job.get("options") or _default_options("standard"))
        store.update_job(job_id, status="researching", stage="researching", progress="正在拆解主题并检索资料", progress_percent=10)
        topic = job["topic"]
        research_pack = collect_research(topic, job, options)
        store.update_job(
            job_id,
            status="writing",
            stage="writing",
            progress=f"{_format_source_label(research_pack)}，正在生成报告正文",
            source_count=research_pack.get("source_count", 0),
            source_status=research_pack.get("source_status", ""),
            source_label=research_pack.get("source_label", ""),
            source_notice=research_pack.get("source_notice", ""),
            progress_percent=45,
        )
        markdown_text = _generate_report_markdown(topic, source_context, job_id, research_pack, options)
        if int(research_pack.get("source_count") or 0) <= 0:
            markdown_text = _strip_unverified_references(markdown_text)
        markdown_text = _ensure_references(markdown_text, research_pack)
        title = _make_title(topic)
        with open(job["md_path"], "w", encoding="utf-8") as f:
            f.write(markdown_text)
        store.update_job(job_id, status="rendering", stage="rendering", progress="正在排版并导出 PDF", progress_percent=80)
        render_html(markdown_text, title, job["html_path"])
        render_pdf(job["html_path"], job["pdf_path"], markdown_text, title)
        if not os.path.isfile(job["pdf_path"]):
            raise RuntimeError("PDF file was not generated")
        job = store.update_job(
            job_id,
            status="done",
            stage="done",
            title=title,
            error="",
            progress="PDF 已生成",
            progress_percent=100,
            source_count=research_pack.get("source_count", 0),
            source_status=research_pack.get("source_status", ""),
            source_label=research_pack.get("source_label", ""),
            source_notice=research_pack.get("source_notice", ""),
        )
        _send(
            channel,
            source_context,
            f"报告已生成：{title}\n任务编号：{job_id}\n模式：{options.get('label', '标准')}\n{_format_source_line(research_pack)}\n下载链接：{_download_url(job)}",
        )
    except Exception as e:
        logger.error(f"[Reports] Job {job_id} failed: {e}", exc_info=True)
        store.update_job(job_id, status="failed", stage="failed", error=str(e), progress_percent=100)
        _send(channel, source_context, f"报告任务 {job_id} 生成失败：{e}")


def _generate_report_markdown(topic: str, source_context, job_id: str, research_pack: dict = None, options: dict = None) -> str:
    research_pack = research_pack or {}
    options = dict(options or _default_options("standard"))
    research_context = format_research_for_prompt(research_pack)
    has_sources = int(research_pack.get("source_count") or 0) > 0
    source_requirement = (
        "3. 对关键事实尽量引用来源编号，例如“根据资料 [2] ...”。"
        if has_sources
        else "3. 当前没有可验证外部来源。不要编造参考文献、政策编号、论文条目或 [1][2] 这类引用编号；请在正文中明确写出“资料限制”。"
    )
    prompt = f"""你是专业研究员。请围绕下面主题生成一份结构完整的中文研究报告草稿。

主题：{topic}
报告模式：{options.get('label', '标准')}
目标篇幅：约 {options.get('target_words', 3000)} 个中文字符，允许根据资料质量上下浮动。

下面是本次任务已经整理出的研究资料，请优先基于这些来源写作。引用来源时使用 [1]、[2] 这样的编号：

{research_context}

要求：
1. 输出 Markdown。
2. 包含：摘要、核心结论、背景与现状、关键问题、典型案例、机会与风险、行动建议、后续研究方向。
{source_requirement}
4. 如果来源不足，请明确写出“资料限制”，不要编造具体数据。
5. 内容要适合直接排版成 PDF，不要输出与报告无关的寒暄。
6. 不要尝试写入或修改系统文件。
"""
    report_context = Context(ContextType.TEXT, prompt, kwargs=dict(getattr(source_context, "kwargs", {}) or {}))
    report_context["session_id"] = f"{source_context.get('session_id', context_user_key(source_context))}__report__{job_id}"
    report_context["channel_type"] = source_context.get("channel_type", "")
    report_context["on_event"] = True
    report_context.kwargs.pop("channel", None)

    try:
        from bridge.bridge import Bridge

        reply = Bridge().fetch_agent_reply(prompt, report_context, clear_history=True)
        content = getattr(reply, "agent_response", None) or getattr(reply, "content", "")
        content = str(content or "").strip()
        if content and getattr(reply, "type", None) != ReplyType.ERROR:
            return content
        if content:
            logger.warning(f"[Reports] Agent returned error-like content, using fallback: {content[:200]}")
    except Exception as e:
        logger.warning(f"[Reports] Agent report generation failed, using fallback: {e}")

    return _fallback_report(topic, research_pack, options)


def _fallback_report(topic: str, research_pack: dict = None, options: dict = None) -> str:
    research_pack = research_pack or {}
    options = dict(options or _default_options("standard"))
    source_count = research_pack.get("source_count", 0)
    source_label = _format_source_label(research_pack)
    return f"""# {topic}研究报告

## 摘要

本报告围绕“{topic}”形成 V4 草稿，采用“{options.get('label', '标准')}”模式，重点梳理研究背景、关键问题、机会风险和行动建议。本次资料状态为：{source_label}；若来源不足，相关结论应作为初步判断继续复核。

## 核心结论

- 该主题需要从市场环境、技术路径、组织落地和风险治理四个角度综合判断。
- 短期价值通常来自效率提升、成本优化和流程标准化。
- 中长期价值取决于数据积累、能力复用、组织协同和持续迭代机制。

## 背景与现状

围绕该主题的实践通常会经历从概念验证到局部落地，再到规模化应用的过程。早期阶段应优先选择边界清晰、收益可衡量、风险可控制的场景。

## 关键问题

1. 目标是否足够明确，是否能拆解成可执行任务。
2. 数据来源是否可靠，是否具备持续更新机制。
3. 技术实现是否能够和现有系统、流程、权限体系结合。
4. 成本、质量、安全和合规是否有明确评估标准。

## 机会与风险

机会主要来自自动化、知识沉淀和决策辅助。风险主要包括结果不稳定、数据质量不足、权限边界不清、过度依赖单一工具等。

## 行动建议

- 先做小范围试点，明确输入、输出、评估指标和负责人。
- 对关键数据和操作权限建立隔离机制。
- 把高质量案例沉淀为模板、流程和可复用能力。
- 建立人工复核机制，避免自动化结果直接进入高风险决策。

## 后续研究方向

建议后续补充真实案例、数据来源、竞品对比、成本测算和落地路线图。

## 资料限制

本报告为 V4 自动生成草稿，已经加入参数化任务、研究计划、来源整理、进度记录和 PDF 交付流程。重要商业或投资决策仍建议补充人工复核。
"""


def _ensure_references(markdown_text: str, research_pack: dict) -> str:
    text = str(markdown_text or "").strip()
    if "## 参考来源" in text or "## 参考资料" in text:
        return text + "\n"
    return text + "\n\n" + references_markdown(research_pack)


def _strip_unverified_references(markdown_text: str) -> str:
    text = str(markdown_text or "").strip()
    text = re.sub(r"\s*##\s*(?:\d+\s*)?(参考文献|参考资料|参考来源)\s*[\s\S]*$", "", text).strip()
    text = re.sub(r"(?<!\!)\[(\d{1,3})\]", "", text)
    text = re.sub(r"（\s*）", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _make_title(topic: str) -> str:
    topic = re.sub(r"\s+", " ", str(topic or "")).strip()
    if topic.endswith("报告"):
        return topic
    return f"{topic}研究报告"


def _download_url(job: dict) -> str:
    base = (
        conf().get("report_public_base_url")
        or conf().get("web_public_base_url")
        or f"http://127.0.0.1:{int(conf().get('web_port', 9899) or 9899)}"
    )
    base = str(base).rstrip("/")
    return f"{base}/api/reports/download/{job['job_id']}?token={job['token']}"


def _format_source_label(research_pack: dict) -> str:
    source_count = int((research_pack or {}).get("source_count") or 0)
    if source_count > 0:
        return f"已整理 {source_count} 个外部来源"
    return (research_pack or {}).get("source_label") or "外部来源待补充"


def _format_source_line(research_pack: dict) -> str:
    source_count = int((research_pack or {}).get("source_count") or 0)
    if source_count > 0:
        return f"来源数量：{source_count}"
    notice = (research_pack or {}).get("source_notice") or "未获取到可验证外部来源，报告已标注资料限制。"
    return f"来源状态：外部来源待补充\n说明：{notice}"


def _format_job_source_line(job: dict) -> str:
    source_count = int((job or {}).get("source_count") or 0)
    if source_count > 0:
        return f"来源数量：{source_count}"
    notice = (job or {}).get("source_notice") or "未获取到可验证外部来源，报告已标注资料限制。"
    return f"来源状态：外部来源待补充\n说明：{notice}"


def _parse_report_options(text: str) -> tuple:
    raw = str(text or "").strip()
    options = _default_options("standard")

    def set_depth(value: str):
        nonlocal options
        depth = _normalize_depth(value)
        options = _default_options(depth)

    def take_number(pattern: str, key: str, minimum: int, maximum: int):
        nonlocal raw
        match = re.search(pattern, raw, flags=re.I)
        if not match:
            return
        try:
            value = max(minimum, min(maximum, int(match.group(1))))
        except Exception:
            return
        options[key] = value
        raw = (raw[:match.start()] + " " + raw[match.end():]).strip()

    prefix_match = re.match(r"^(快速|标准|深度)报告\s*[：:]\s*(.+)$", raw)
    if prefix_match:
        set_depth(prefix_match.group(1))
        raw = prefix_match.group(2).strip()

    depth_match = re.search(r"(?:--?深度|--?模式|深度|模式)\s*[=:：]?\s*(快速|快|标准|普通|深度|深入|详细|完整)", raw, flags=re.I)
    if depth_match:
        set_depth(depth_match.group(1))
        raw = (raw[:depth_match.start()] + " " + raw[depth_match.end():]).strip()
    else:
        edge_match = re.search(r"(?:^|\s)(快速|标准|深度)(?:报告)?(?:\s|$)", raw)
        if edge_match:
            set_depth(edge_match.group(1))
            raw = (raw[:edge_match.start()] + " " + raw[edge_match.end():]).strip()

    take_number(r"(?:--?字数|字数|篇幅)\s*[=:：]?\s*(\d{3,5})", "target_words", 800, 12000)
    take_number(r"(\d{3,5})\s*字", "target_words", 800, 12000)
    take_number(r"(?:--?来源|来源|资料)\s*[=:：]?\s*(\d{1,2})", "max_sources", 1, 20)

    options["max_fetched_sources"] = min(int(options.get("max_sources", 10)), int(options.get("max_fetched_sources", 5)))
    raw = re.sub(r"\s+", " ", raw).strip(" ：:\n\t")
    return raw, options


def _normalize_depth(value: str) -> str:
    value = str(value or "").strip().lower()
    if value in ("快速", "快", "fast"):
        return "fast"
    if value in ("深度", "深入", "详细", "完整", "deep"):
        return "deep"
    return "standard"


def _default_options(depth: str) -> dict:
    depth = _normalize_depth(depth)
    options = dict(DEPTH_PRESETS.get(depth, DEPTH_PRESETS["standard"]))
    options["depth"] = depth
    return options


def _report_help_text() -> str:
    return (
        "报告命令用法：\n"
        "1. /报告 主题\n"
        "2. /报告 主题 --模式 深度 --字数 5000 --来源 15\n"
        "3. /报告状态 任务编号\n"
        "4. /报告列表\n\n"
        "模式可选：快速、标准、深度。"
    )


def _send(channel, context, text: str):
    try:
        channel._send(Reply(ReplyType.TEXT, text), context)
    except Exception:
        logger.exception("[Reports] Failed to send WeChat report message")
