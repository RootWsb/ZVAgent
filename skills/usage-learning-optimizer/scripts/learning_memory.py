#!/usr/bin/env python3
"""Maintain compact usage-learning files for the vertical assistant."""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
from pathlib import Path


PROFILE_FILES = {
    "user_preferences.md": """# User Preferences

> Purpose: stable preferences that help the assistant answer with less repeated instruction.

## Global

- Language: Chinese by default unless the user asks otherwise.
- Style: conclusion first, evidence second, then mechanism, risk, and next step.
- Default depth: brief unless the user asks for quick, deep, or archive.

## Research

- Include method, contribution, limitation, and reproducibility notes for paper analysis.

## Crypto

- Use read-only data workflows.
- Always include risk and uncertainty framing.
- Do not provide deterministic buy/sell instructions.

## Economics

- Prefer official or primary data sources.
- Use scenarios instead of single-point forecasts.

## AI Tech

- Prefer official blogs, papers, repos, benchmarks, and implementation details.
- Highlight engineering implications and reproducibility when relevant.

## Explicit Preferences

- Add new stable preferences here as short bullets.
""",
    "task_patterns.md": """# Task Patterns

> Purpose: reusable templates for recurring work. Keep this file short.

## AI Paper Note

Use: conclusion, problem, core idea, method, experiments, linked code/models/datasets, reproducibility, limitations, next steps.

## Crypto Risk Review

Use: market context, catalyst, on-chain/social evidence, scenario risks, invalidation signals, no buy/sell command.

## Macro Data Analysis

Use: data surprise, historical context, transmission mechanism, cross-asset impact, scenarios, watchlist.

## AI Tech Digest

Use: model releases, papers, repos, engineering posts, benchmarks, product/API changes, what to test next.

## Research Literature Map

Use: search scope, inclusion/exclusion criteria, clusters, key papers, disagreements, gaps, reading order.
""",
    "context_budget.md": """# Context Budget

> Purpose: choose the smallest useful context and output size.

## Modes

- quick: <= 300 Chinese chars or 5 bullets; no broad background.
- brief: 600-1200 Chinese chars; default for most analysis.
- deep: use only when the user asks for deep detail, comparison, strategy, or reproduction.
- archive: durable Markdown for `knowledge/`; concise but complete.
- For non-trivial requests, use `task-budget-router` to choose mode and budgets before expanding work.

## Retrieval Budget

- First check `knowledge/index.md` for relevant local pages.
- Read at most 3 local knowledge pages before answering unless the task explicitly needs a review.
- For current information, fetch primary sources first and add specialist sources only if needed.
- Do not restate full old notes; link to them and summarize only the delta.

## Archive Budget

- Archive only stable insights, reusable templates, source-backed briefs, and explicit preferences.
- Do not archive transient chat unless it changes future behavior.
""",
    "feedback_log.md": """# Feedback Log

Append-only. Newest entries at the bottom.
""",
}


def resolve_workspace(raw: str | None) -> Path:
    value = raw or os.environ.get("ZV_AGENT_WORKSPACE") or "~/zvagent"
    return Path(value).expanduser().resolve()


def profile_dir(workspace: Path) -> Path:
    return workspace / "knowledge" / "profile"


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def append_once(path: Path, line: str) -> bool:
    content = read_text(path)
    if line in content:
        return False
    with path.open("a", encoding="utf-8", newline="\n") as f:
        if content and not content.endswith("\n"):
            f.write("\n")
        f.write(line.rstrip() + "\n")
    return True


def init_workspace(workspace: Path, verbose: bool = True) -> None:
    pdir = profile_dir(workspace)
    pdir.mkdir(parents=True, exist_ok=True)
    for name, template in PROFILE_FILES.items():
        path = pdir / name
        if not path.exists():
            path.write_text(template, encoding="utf-8", newline="\n")

    kdir = workspace / "knowledge"
    kdir.mkdir(parents=True, exist_ok=True)
    index = kdir / "index.md"
    if not index.exists():
        index.write_text("# Knowledge Index\n", encoding="utf-8", newline="\n")

    entries = [
        "## Profile",
        "- [User Preferences](profile/user_preferences.md) - stable user preferences and domain tastes.",
        "- [Task Patterns](profile/task_patterns.md) - reusable task templates and routing hints.",
        "- [Context Budget](profile/context_budget.md) - answer modes, retrieval depth, and token-saving rules.",
        "- [Feedback Log](profile/feedback_log.md) - append-only raw feedback for future refinement.",
    ]
    content = read_text(index)
    if "## Profile" not in content:
        with index.open("a", encoding="utf-8", newline="\n") as f:
            if content and not content.endswith("\n"):
                f.write("\n")
            f.write("\n".join(entries) + "\n")

    log = kdir / "log.md"
    if not log.exists():
        log.write_text("# Knowledge Log\n", encoding="utf-8", newline="\n")
    today = _dt.date.today().isoformat()
    append_once(log, f"## [{today}] maintain | usage-learning profile initialized")
    if verbose:
        print(f"Initialized usage-learning profile at {pdir}")


def infer_mode(prompt: str) -> str:
    text = prompt.lower()
    quick_terms = ["简单", "快速", "一句话", "简短", "短一点", "短点", "短些", "太长", "quick", "tl;dr", "tldr"]
    deep_terms = ["深入", "详细", "系统", "全面", "长文", "deep", "review", "复盘", "复现"]
    archive_terms = ["入库", "归档", "保存", "沉淀", "archive", "knowledge"]
    if any(term in text for term in archive_terms):
        return "archive"
    if any(term in text for term in quick_terms):
        return "quick"
    if any(term in text for term in deep_terms):
        return "deep"
    return "brief"


def record_feedback(workspace: Path, feedback: str, domain: str, task_type: str) -> None:
    init_workspace(workspace, verbose=False)
    today = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    safe_feedback = " ".join(feedback.split())
    line = f"- {today} | domain={domain or 'general'} | task={task_type or 'general'} | {safe_feedback}"
    append_once(profile_dir(workspace) / "feedback_log.md", line)

    lower = safe_feedback.lower()
    suggestions: list[str] = []
    if any(x in lower for x in ["短", "简洁", "太长", "short", "concise"]):
        suggestions.append("- Consider updating `context_budget.md`: prefer quick/brief for similar tasks.")
    if any(x in lower for x in ["详细", "深入", "展开", "deep"]):
        suggestions.append("- Consider updating `context_budget.md`: allow deep mode for this task type.")
    if any(x in lower for x in ["结构", "模板", "格式", "pattern", "template"]):
        suggestions.append("- Consider updating `task_patterns.md`: preserve this output structure.")
    if any(x in lower for x in ["以后", "总是", "默认", "记住", "preference"]):
        suggestions.append("- Consider updating `user_preferences.md`: add this as a stable preference.")

    print("Recorded feedback.")
    if suggestions:
        print("\nSuggested follow-up edits:")
        print("\n".join(suggestions))


def select_sections(text: str, headings: list[str], max_lines: int) -> str:
    if not text:
        return ""
    lines = text.splitlines()
    keep: list[str] = []
    active = False
    for line in lines:
        if line.startswith("# "):
            keep.append(line)
            continue
        if line.startswith("## "):
            active = any(h.lower() in line.lower() for h in headings) or "global" in line.lower() or "modes" in line.lower()
        if active:
            keep.append(line)
    if not keep:
        keep = lines[:max_lines]
    return "\n".join(keep[:max_lines])


def build_context(workspace: Path, domain: str, task_type: str, max_lines: int) -> None:
    init_workspace(workspace, verbose=False)
    pdir = profile_dir(workspace)
    headings = [domain or "", task_type or ""]
    parts = []
    for filename in ("user_preferences.md", "task_patterns.md", "context_budget.md"):
        content = select_sections(read_text(pdir / filename), headings, max_lines=max(10, max_lines // 3))
        if content:
            parts.append(f"## {filename}\n{content}")
    print("\n\n".join(parts))


def compact_feedback(workspace: Path) -> None:
    init_workspace(workspace, verbose=False)
    log = read_text(profile_dir(workspace) / "feedback_log.md")
    bullets = []
    for line in log.splitlines():
        if not line.startswith("- "):
            continue
        text = re.sub(r"^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} \| .*? \| ", "", line)
        if any(k in text for k in ["以后", "默认", "总是", "记住"]):
            bullets.append("- " + text)
    if not bullets:
        print("No stable preference candidates found.")
        return
    print("Stable preference candidates:")
    print("\n".join(dict.fromkeys(bullets)))


def main() -> None:
    parser = argparse.ArgumentParser(description="Usage-learning profile manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("--workspace")

    p_mode = sub.add_parser("mode")
    p_mode.add_argument("--prompt", required=True)

    p_feedback = sub.add_parser("feedback")
    p_feedback.add_argument("--feedback", required=True)
    p_feedback.add_argument("--domain", default="general")
    p_feedback.add_argument("--task-type", default="general")
    p_feedback.add_argument("--workspace")

    p_context = sub.add_parser("context")
    p_context.add_argument("--domain", default="general")
    p_context.add_argument("--task-type", default="general")
    p_context.add_argument("--workspace")
    p_context.add_argument("--max-lines", type=int, default=80)

    p_compact = sub.add_parser("compact-feedback")
    p_compact.add_argument("--workspace")

    args = parser.parse_args()
    if args.cmd == "mode":
        print(infer_mode(args.prompt))
        return

    workspace = resolve_workspace(getattr(args, "workspace", None))
    if args.cmd == "init":
        init_workspace(workspace)
    elif args.cmd == "feedback":
        record_feedback(workspace, args.feedback, args.domain, args.task_type)
    elif args.cmd == "context":
        build_context(workspace, args.domain, args.task_type, args.max_lines)
    elif args.cmd == "compact-feedback":
        compact_feedback(workspace)


if __name__ == "__main__":
    main()
