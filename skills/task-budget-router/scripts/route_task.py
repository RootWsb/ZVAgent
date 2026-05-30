#!/usr/bin/env python3
"""Route a user request into a compact execution budget."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict


DOMAIN_KEYWORDS = {
    "research": [
        "paper", "arxiv", "doi", "literature", "review", "formula", "reproduce",
        "hypothesis", "proposal", "research question", "thesis",
        "选题", "假设", "课题", "实验设计",
        "experiment", "论文", "文献", "公式", "复现", "实验", "综述", "引用",
    ],
    "crypto": [
        "btc", "bitcoin", "eth", "ethereum", "defi", "token", "wallet", "on-chain",
        "tokenomics", "unlock", "vesting", "hack", "exploit", "depeg",
        "代币经济", "解锁", "漏洞", "被盗", "攻击", "脱锚",
        "binance", "coinbase", "airdrop", "staking", "币", "加密", "链上", "钱包",
        "交易所", "代币", "空投",
    ],
    "economics": [
        "cpi", "gdp", "fed", "fomc", "inflation", "jobs", "payroll", "rate",
        "earnings", "filing", "guidance", "equity", "stock", "financial news",
        "财报", "公告", "指引", "金融消息", "股票",
        "treasury", "yield", "fx", "commodity", "央行", "美联储", "通胀", "利率",
        "就业", "财政", "国债", "汇率", "大宗",
    ],
    "ai-tech": [
        "ai", "llm", "rag", "agent", "inference", "training", "benchmark",
        "model", "github", "hugging face", "transformer", "模型", "推理", "训练",
        "评测", "开源", "技术文章", "智能体",
    ],
}

MODE_KEYWORDS = {
    "quick": ["quick", "short", "tl;dr", "tldr", "briefly", "简单", "快速", "一句话", "简短", "短一点", "短点", "太长"],
    "deep": ["deep", "detailed", "systematic", "comprehensive", "strategy", "compare", "reproduce", "深入", "详细", "系统", "全面", "策略", "对比", "复现"],
    "archive": ["archive", "save", "入库", "归档", "保存", "沉淀"],
}

CURRENT_KEYWORDS = [
    "latest", "today", "yesterday", "this week", "current", "price", "ranking",
    "release", "policy", "api", "regulation", "news", "最新", "今天", "昨日",
    "本周", "当前", "价格", "排行榜", "发布", "政策", "监管", "新闻",
]

FEEDBACK_KEYWORDS = ["以后", "下次", "记住", "偏好", "太长", "太短", "格式", "模板", "preference", "remember"]
KNOWLEDGE_KEYWORDS = ["knowledge", "local notes", "知识库", "笔记", "已有记录", "历史记录", "之前"]
SCHEDULE_KEYWORDS = ["daily", "weekly", "monthly", "schedule", "日报", "周报", "月报", "定时", "每天", "每周"]


WRITING_KEYWORDS = [
    "writing", "rewrite", "polish", "draft", "copyedit", "standardize",
    "standardise", "style guide", "structure", "paragraph", "memo",
    "academic writing", "technical writing", "market report", "evidence-based",
    "citation", "footnote", "knowledge note", "markdown note",
    "\u5199\u4f5c", "\u6539\u5199", "\u6da6\u8272", "\u89c4\u8303",
    "\u6210\u6587", "\u6587\u98ce", "\u8bed\u6c14", "\u8868\u8ff0",
    "\u6458\u8981", "\u5f15\u8a00", "\u76f8\u5173\u5de5\u4f5c",
    "\u5f00\u9898", "\u6bd5\u4e1a\u8bba\u6587", "\u5b66\u672f\u5199\u4f5c",
    "\u5f15\u7528", "\u8bc1\u636e", "\u51fa\u5904", "\u7814\u62a5",
    "\u62a5\u544a", "\u6280\u672f\u6587\u7ae0", "\u6280\u672f\u89e3\u8bfb",
    "\u77e5\u8bc6\u7b14\u8bb0", "\u5f52\u6863\u7b14\u8bb0",
]

DOMAIN_KEYWORDS["writing"] = WRITING_KEYWORDS
DOMAIN_KEYWORDS["research"].extend([
    "\u8bba\u6587", "\u6587\u732e", "\u7efc\u8ff0", "\u5b9e\u9a8c",
    "\u8bfe\u9898", "\u5047\u8bbe", "\u5f00\u9898", "\u5b66\u672f",
])
DOMAIN_KEYWORDS["crypto"].extend([
    "\u52a0\u5bc6", "\u94fe\u4e0a", "\u94b1\u5305", "\u4ee3\u5e01",
    "\u89e3\u9501", "\u7a7a\u6295", "\u4ea4\u6613\u6240",
])
DOMAIN_KEYWORDS["economics"].extend([
    "\u5b8f\u89c2", "\u7ecf\u6d4e", "\u91d1\u878d", "\u80a1\u7968",
    "\u8d22\u62a5", "\u5229\u7387", "\u901a\u80c0", "\u7f8e\u8054\u50a8",
    "\u56fd\u503a", "\u6c47\u7387",
])
DOMAIN_KEYWORDS["ai-tech"].extend([
    "\u6a21\u578b", "\u63a8\u7406", "\u8bad\u7ec3", "\u8bc4\u6d4b",
    "\u5f00\u6e90", "\u6280\u672f\u6587\u7ae0", "\u667a\u80fd\u4f53",
])
MODE_KEYWORDS["archive"].extend([
    "\u5f52\u6863", "\u5165\u5e93", "\u4fdd\u5b58",
])
KNOWLEDGE_KEYWORDS.extend([
    "\u77e5\u8bc6\u5e93", "\u77e5\u8bc6\u7b14\u8bb0", "\u7b14\u8bb0",
    "\u6807\u7b7e", "\u53cc\u94fe", "\u76f8\u5173\u94fe\u63a5",
])


@dataclass
class Budget:
    domain: str
    mode: str
    primary_skills: list[str]
    local_knowledge_pages: int
    fresh_sources: int
    output_budget: str
    archive: bool
    quality_gate: bool
    current_data: bool
    notes: list[str]


def normalize(text: str) -> str:
    return text.lower()


def count_hits(text: str, keywords: list[str]) -> int:
    return sum(1 for keyword in keywords if keyword.lower() in text)


def infer_domains(text: str) -> list[str]:
    scores = {
        domain: count_hits(text, keywords)
        for domain, keywords in DOMAIN_KEYWORDS.items()
    }
    matched = [domain for domain, score in scores.items() if score > 0]
    if len(matched) >= 2:
        return matched
    if matched:
        return matched
    return ["general"]


def infer_mode(text: str) -> str:
    if count_hits(text, MODE_KEYWORDS["archive"]):
        return "archive"
    if count_hits(text, MODE_KEYWORDS["quick"]):
        return "quick"
    if count_hits(text, MODE_KEYWORDS["deep"]):
        return "deep"
    return "brief"


def output_budget(mode: str) -> str:
    return {
        "quick": "<= 300 Chinese chars or 5 bullets",
        "brief": "600-1200 Chinese chars",
        "deep": "structured long answer; expand only where useful",
        "archive": "concise Markdown suitable for knowledge/",
    }[mode]


def base_budgets(mode: str) -> tuple[int, int]:
    return {
        "quick": (1, 2),
        "brief": (3, 4),
        "deep": (8, 8),
        "archive": (8, 8),
    }[mode]


def skill_for_domain(domain: str) -> list[str]:
    return {
        "research": ["research-assistant"],
        "crypto": ["crypto-news"],
        "economics": ["economic-analysis"],
        "ai-tech": ["ai-tech-digest"],
        "writing": [],
        "cross-domain": ["vertical-research-orchestrator"],
        "general": ["vertical-research-orchestrator"],
    }.get(domain, ["vertical-research-orchestrator"])


def enrich_skills(text: str, domains: list[str], mode: str, current: bool, archive: bool) -> list[str]:
    skills: list[str] = []
    domain = "cross-domain" if len(domains) > 1 else domains[0]
    if domain == "cross-domain":
        skills.append("vertical-research-orchestrator")
        for item in domains:
            skills.extend(skill_for_domain(item))
    else:
        skills.extend(skill_for_domain(domain))

    if "research" in domains:
        if any(k in text for k in ["doi", "arxiv", "pubmed", "semantic scholar", "openalex", "论文", "文献"]):
            skills.append("paper-lookup")
        if any(k in text for k in ["literature", "review", "综述", "相关工作"]):
            skills.append("literature-review")
        if any(k in text for k in ["hypothesis", "research question", "proposal", "thesis", "选题", "假设", "课题"]):
            skills.append("research-hypothesis-planner")
        if any(k in text for k in ["ablation", "baseline", "metric", "evaluation", "control", "实验设计", "消融", "指标"]):
            skills.append("experiment-design-reviewer")
    if "writing" in domains:
        writing_skill_count = len(skills)
        if any(k in text for k in [
            "academic", "paper", "abstract", "introduction", "related work", "thesis",
            "proposal", "\u8bba\u6587", "\u6458\u8981", "\u5f15\u8a00",
            "\u76f8\u5173\u5de5\u4f5c", "\u5f00\u9898", "\u6bd5\u4e1a\u8bba\u6587",
            "\u5b66\u672f",
        ]):
            skills.append("academic-writing-standardizer")
        if any(k in text for k in [
            "citation", "cite", "evidence", "source-backed", "footnote",
            "\u5f15\u7528", "\u8bc1\u636e", "\u51fa\u5904", "\u6765\u6e90",
            "\u811a\u6ce8",
        ]):
            skills.append("evidence-citation-writer")
        if any(k in text for k in [
            "market report", "macro note", "financial report", "investment memo",
            "brief", "memo", "\u7814\u62a5", "\u62a5\u544a", "\u5e02\u573a\u7b80\u62a5",
            "\u6295\u7814", "\u5b8f\u89c2", "\u52a0\u5bc6", "\u91d1\u878d",
        ]):
            skills.append("market-report-writer")
        if any(k in text for k in [
            "ai", "llm", "rag", "agent", "benchmark", "repo", "model",
            "technical article", "explainer", "\u6280\u672f\u6587\u7ae0",
            "\u6280\u672f\u89e3\u8bfb", "\u6a21\u578b", "\u5f00\u6e90",
        ]):
            skills.append("ai-technical-writing")
        if any(k in text for k in [
            "knowledge note", "markdown note", "wiki", "archive", "tag", "backlink",
            "\u77e5\u8bc6\u7b14\u8bb0", "\u5f52\u6863", "\u6807\u7b7e",
            "\u53cc\u94fe", "\u77e5\u8bc6\u5e93",
        ]):
            skills.append("knowledge-note-standardizer")
        if len(skills) == writing_skill_count:
            skills.append("academic-writing-standardizer")
    if "crypto" in domains and current:
        skills.append("surf")
    if "crypto" in domains:
        if any(k in text for k in ["tokenomics", "unlock", "vesting", "fdv", "governance", "token due", "代币经济", "解锁", "尽调"]):
            skills.append("token-due-diligence")
        if any(k in text for k in ["hack", "exploit", "security incident", "bridge failure", "depeg", "漏洞", "被盗", "攻击", "脱锚"]):
            skills.append("crypto-security-incident")
    if "economics" in domains:
        if any(k in text for k in ["treasury", "fiscal", "国债", "财政"]):
            skills.append("usfiscaldata")
        if any(k in text for k in ["统计", "回归", "显著", "correlation", "regression"]):
            skills.append("statistical-analysis")
        if any(k in text for k in ["earnings", "filing", "10-k", "10-q", "8-k", "s-1", "guidance", "财报", "公告", "指引"]):
            skills.append("earnings-filing-reader")
        if any(k in text for k in ["financial news", "market impact", "market reaction", "sector shock", "credit spread", "市场影响", "金融消息", "为什么涨", "为什么跌"]):
            skills.append("financial-news-impact")
    if "ai-tech" in domains:
        if any(k in text for k in ["paper", "arxiv", "论文", "hugging face"]):
            skills.append("huggingface-papers")
        if any(k in text for k in ["dataset", "数据集"]):
            skills.append("huggingface-datasets")
        if any(k in text for k in ["benchmark", "leaderboard", "eval", "evaluation", "sota", "评测", "榜单"]):
            skills.append("ai-benchmark-auditor")
        if any(k in text for k in ["repo", "repository", "github", "open source", "framework", "开源项目", "仓库"]):
            skills.append("ai-open-source-evaluator")
    if current:
        skills.append("source-registry")
    if any(k in text for k in FEEDBACK_KEYWORDS):
        skills.append("usage-learning-optimizer")
        skills.append("feedback-template-evolver")
    if any(k in text for k in KNOWLEDGE_KEYWORDS):
        skills.append("knowledge-note-standardizer")
        skills.append("knowledge-compression-indexer")
    if archive:
        skills.append("knowledge-wiki")
    if mode in {"archive", "deep"} or any(k in text for k in SCHEDULE_KEYWORDS):
        skills.append("quality-guardrails")

    deduped: list[str] = []
    for skill in skills:
        if skill not in deduped:
            deduped.append(skill)
    return deduped


def route(prompt: str) -> Budget:
    text = normalize(prompt)
    raw_domains = infer_domains(text)
    domain = "cross-domain" if len(raw_domains) > 1 else raw_domains[0]
    mode = infer_mode(text)
    current = count_hits(text, CURRENT_KEYWORDS) > 0
    archive = mode == "archive" or count_hits(text, SCHEDULE_KEYWORDS) > 0
    local_pages, fresh_sources = base_budgets(mode)

    if current:
        fresh_sources = max(fresh_sources, 4 if mode == "brief" else fresh_sources)
    else:
        fresh_sources = {
            "quick": 0,
            "brief": min(fresh_sources, 2),
            "deep": min(fresh_sources, 4),
            "archive": min(fresh_sources, 4),
        }[mode]

    if any(domain in raw_domains for domain in ["research", "ai-tech"]) and mode in {"deep", "archive"}:
        fresh_sources = max(fresh_sources, 4)

    if count_hits(text, KNOWLEDGE_KEYWORDS):
        local_pages = max(local_pages, 5 if mode != "quick" else 2)
        if not current:
            fresh_sources = 0

    quality_gate = archive or mode == "deep" or "quality-guardrails" in text
    notes = []
    if any(item in raw_domains for item in ["crypto", "economics"]):
        notes.append("Include risk and uncertainty framing for market-sensitive analysis.")
    if current:
        notes.append("Use source-registry before fetching current facts.")
    if count_hits(text, FEEDBACK_KEYWORDS):
        notes.append("Record stable feedback with usage-learning-optimizer and create reusable-change proposals with feedback-template-evolver.")
    if local_pages >= 5:
        notes.append("Use knowledge-compression-indexer to choose a small local context pack.")

    return Budget(
        domain=domain,
        mode=mode,
        primary_skills=enrich_skills(text, raw_domains, mode, current, archive),
        local_knowledge_pages=local_pages,
        fresh_sources=fresh_sources,
        output_budget=output_budget(mode),
        archive=archive,
        quality_gate=quality_gate,
        current_data=current,
        notes=notes,
    )


def render_markdown(budget: Budget) -> str:
    lines = [
        "# Task Budget",
        "",
        f"- Domain: {budget.domain}",
        f"- Mode: {budget.mode}",
        f"- Primary skills: {', '.join(budget.primary_skills)}",
        f"- Local knowledge budget: {budget.local_knowledge_pages} page(s)",
        f"- Fresh source budget: {budget.fresh_sources} source(s)",
        f"- Output budget: {budget.output_budget}",
        f"- Archive: {'yes' if budget.archive else 'no'}",
        f"- Quality gate: {'yes' if budget.quality_gate else 'no'}",
        f"- Current data: {'yes' if budget.current_data else 'no'}",
    ]
    if budget.notes:
        lines.append("")
        lines.append("## Notes")
        for note in budget.notes:
            lines.append(f"- {note}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Route a task into a compact execution budget")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    budget = route(args.prompt)
    if args.format == "json":
        print(json.dumps(asdict(budget), ensure_ascii=False, indent=2))
    else:
        print(render_markdown(budget))


if __name__ == "__main__":
    main()
