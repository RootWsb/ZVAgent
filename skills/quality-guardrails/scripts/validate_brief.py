#!/usr/bin/env python3
"""Validate a vertical research brief Markdown file."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List


REQUIRED_SECTION_ALIASES = {
    "conclusion": ["结论", "一句话主线", "主线判断", "数据结论", "质量结论"],
    "evidence": ["依据", "关键事实", "来源", "数据与政策", "Source", "Sources"],
    "risk": ["风险/不确定性", "风险", "风险因素", "情景与风险", "限制", "不确定性"],
    "next": ["下一步", "接下来观察", "观察清单", "下期观察", "建议修复"],
}

DOMAIN_KEYWORDS = {
    "crypto": ["BTC", "ETH", "crypto", "加密", "币", "DeFi", "token"],
    "economics": ["CPI", "GDP", "央行", "利率", "宏观", "Fed", "就业", "通胀"],
    "ai-tech": ["AI", "模型", "API", "GitHub", "RAG", "Agent", "推理", "训练"],
    "research": ["论文", "arXiv", "实验", "复现", "paper", "repo"],
    "cross-domain": ["跨领域", "宏观", "加密", "AI", "技术"],
}

BUY_SELL_PATTERNS = [
    r"必须\s*(买|卖|做多|做空)",
    r"肯定\s*(上涨|下跌|翻倍)",
    r"all\s*in",
    r"梭哈",
    r"稳赚",
]


def has_heading(text: str, aliases: List[str]) -> bool:
    headings = re.findall(r"^#{1,6}\s+(.+?)\s*$", text, flags=re.MULTILINE)
    return any(any(alias.lower() in heading.lower() for alias in aliases) for heading in headings)


def has_source(text: str) -> bool:
    lowered = text.lower()
    if "pending source verification" in lowered:
        return False

    source_blocks = re.findall(r"^>\s*Source:\s*(.+)$", text, flags=re.MULTILINE | re.IGNORECASE)
    meaningful_source_block = any(
        "automated" not in block.lower() and "draft" not in block.lower()
        for block in source_blocks
    )

    return bool(
        re.search(r"https?://", text)
        or meaningful_source_block
        or re.search(r"`?knowledge/[^`\s]+", text)
        or re.search(r"`?[\w./\\-]+\.(md|py|pdf|ipynb|json)`?", text, flags=re.IGNORECASE)
    )


def mentions_archive(text: str) -> bool:
    return "knowledge/index.md" in text and "knowledge/log.md" in text


def has_risk_framing(text: str) -> bool:
    risk_terms = ["风险", "不确定", "不是投资建议", "研究分析", "情景", "invalidation", "假设"]
    return any(term.lower() in text.lower() for term in risk_terms)


def has_unsafe_financial_claim(text: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in BUY_SELL_PATTERNS)


def infer_domain(text: str) -> str:
    scores: Dict[str, int] = {}
    lower = text.lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        scores[domain] = sum(1 for keyword in keywords if keyword.lower() in lower)
    best = max(scores, key=scores.get)
    return best if scores[best] else "unknown"


def validate(text: str, domain: str | None, require_sources: bool, require_archive: bool) -> Dict:
    issues: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []
    inferred_domain = domain or infer_domain(text)

    for key, aliases in REQUIRED_SECTION_ALIASES.items():
        if not has_heading(text, aliases):
            issues.append({
                "code": f"missing_{key}_section",
                "message": f"Missing required section equivalent: {', '.join(aliases[:3])}",
            })

    source_present = has_source(text)
    if require_sources and not source_present:
        issues.append({"code": "missing_sources", "message": "No source URL, Source block, local path, or knowledge citation found."})
    elif not source_present:
        warnings.append({"code": "weak_sources", "message": "No explicit source found; acceptable only for drafts or non-current answers."})

    if inferred_domain in {"crypto", "economics"}:
        if has_unsafe_financial_claim(text):
            issues.append({"code": "unsafe_financial_claim", "message": "Contains deterministic buy/sell or guaranteed-return language."})
        if not has_risk_framing(text):
            issues.append({"code": "missing_financial_risk_framing", "message": "Crypto/economic output needs risk framing."})

    if inferred_domain == "ai-tech":
        latest_terms = ["最新", "today", "release", "发布", "API", "模型"]
        if any(term.lower() in text.lower() for term in latest_terms) and not source_present:
            issues.append({"code": "ai_current_claim_without_source", "message": "Current AI/model/API claim needs source evidence."})

    if require_archive and not mentions_archive(text):
        warnings.append({"code": "archive_not_confirmed", "message": "No knowledge/index.md and knowledge/log.md update confirmation found."})

    score = 100 - len(issues) * 20 - len(warnings) * 5
    score = max(0, score)
    status = "pass" if not issues and score >= 85 else "warn" if not issues else "fail"

    return {
        "status": status,
        "score": score,
        "domain": inferred_domain,
        "issues": issues,
        "warnings": warnings,
    }


def render_markdown(result: Dict) -> str:
    lines = [
        "## 质量结论",
        f"- Status: {result['status']}",
        f"- Score: {result['score']}",
        f"- Domain: {result['domain']}",
        "",
        "## 问题",
    ]
    if result["issues"]:
        lines.extend(f"- {item['code']}: {item['message']}" for item in result["issues"])
    else:
        lines.append("- No blocking issues.")

    lines.extend(["", "## 警告"])
    if result["warnings"]:
        lines.extend(f"- {item['code']}: {item['message']}" for item in result["warnings"])
    else:
        lines.append("- No warnings.")

    lines.extend([
        "",
        "## 是否可以发布",
        "可以发布。" if result["status"] == "pass" else "建议修复后发布。" if result["status"] == "warn" else "不建议发布，需先修复阻断问题。",
    ])
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Markdown file to validate")
    parser.add_argument("--domain", choices=["ai-tech", "crypto", "economics", "research", "cross-domain"])
    parser.add_argument("--require-sources", action="store_true")
    parser.add_argument("--require-archive", action="store_true")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    text = Path(args.path).read_text(encoding="utf-8")
    result = validate(text, args.domain, args.require_sources, args.require_archive)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(result), end="")


if __name__ == "__main__":
    main()
