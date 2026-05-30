#!/usr/bin/env python3
"""Create and apply reviewable feedback/template evolution proposals."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path


PROFILE_TEMPLATES = {
    "user_preferences.md": """# User Preferences

> Purpose: stable preferences that help the assistant answer with less repeated instruction.

## Global

- Language: Chinese by default unless the user asks otherwise.
- Style: conclusion first, evidence second, then mechanism, risk, and next step.
- Default depth: brief unless the user asks for quick, deep, or archive.

## Explicit Preferences

- Add new stable preferences here as short bullets.
""",
    "task_patterns.md": """# Task Patterns

> Purpose: reusable templates for recurring work. Keep this file short.
""",
    "context_budget.md": """# Context Budget

> Purpose: choose the smallest useful context and output size.

## Modes

- quick: <= 300 Chinese chars or 5 bullets; no broad background.
- brief: 600-1200 Chinese chars; default for most analysis.
- deep: use only when the user asks for deep detail, comparison, strategy, or reproduction.
- archive: durable Markdown for `knowledge/`; concise but complete.
""",
    "feedback_log.md": """# Feedback Log

Append-only. Newest entries at the bottom.
""",
    "template_evolution.md": """# Template Evolution

> Purpose: accepted changes derived from user feedback.

## Accepted Changes
""",
}


@dataclass
class Proposal:
    proposal_id: str
    created_at: str
    feedback: str
    domain: str
    task_type: str
    target_file: str
    target_section: str
    bullet: str
    rationale: str
    status: str = "pending"


def workspace_path(raw: str | None) -> Path:
    value = raw or os.environ.get("ZV_AGENT_WORKSPACE") or "~/zvagent"
    return Path(value).expanduser().resolve()


def knowledge_dir(workspace: Path) -> Path:
    return workspace / "knowledge"


def profile_dir(workspace: Path) -> Path:
    return knowledge_dir(workspace) / "profile"


def proposals_dir(workspace: Path) -> Path:
    return profile_dir(workspace) / "proposals"


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def append_once(path: Path, line: str) -> bool:
    content = read_text(path)
    if line in content:
        return False
    with path.open("a", encoding="utf-8", newline="\n") as f:
        if content and not content.endswith("\n"):
            f.write("\n")
        f.write(line.rstrip() + "\n")
    return True


def init(workspace: Path, verbose: bool = True) -> None:
    pdir = profile_dir(workspace)
    pdir.mkdir(parents=True, exist_ok=True)
    proposals_dir(workspace).mkdir(parents=True, exist_ok=True)
    for name, template in PROFILE_TEMPLATES.items():
        path = pdir / name
        if not path.exists():
            write_text(path, template)

    kdir = knowledge_dir(workspace)
    index = kdir / "index.md"
    if not index.exists():
        write_text(index, "# Knowledge Index\n")
    content = read_text(index)
    profile_entries = [
        "## Profile",
        "- [Template Evolution](profile/template_evolution.md) - accepted feedback-driven template and preference changes.",
    ]
    if "Template Evolution" not in content:
        with index.open("a", encoding="utf-8", newline="\n") as f:
            if content and not content.endswith("\n"):
                f.write("\n")
            if "## Profile" not in content:
                f.write("\n".join(profile_entries) + "\n")
            else:
                f.write("- [Template Evolution](profile/template_evolution.md) - accepted feedback-driven template and preference changes.\n")

    log = kdir / "log.md"
    if not log.exists():
        write_text(log, "# Knowledge Log\n")
    today = dt.date.today().isoformat()
    append_once(log, f"## [{today}] maintain | feedback template evolution initialized")
    if verbose:
        print(f"Initialized feedback template evolution at {pdir}")


def stable_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]


def clean_feedback(value: str) -> str:
    return " ".join(value.strip().split())


def infer_targets(feedback: str, domain: str, task_type: str) -> list[tuple[str, str, str, str]]:
    text = feedback.lower()
    domain_label = domain if domain and domain != "general" else "Global"
    task_label = task_type if task_type and task_type != "general" else "General"
    targets: list[tuple[str, str, str, str]] = []

    if any(k in text for k in ["太长", "短一点", "短点", "简短", "short", "concise"]):
        targets.append((
            "context_budget.md",
            "Modes",
            f"For {domain_label}/{task_label}, prefer quick or brief output unless the user asks for depth.",
            "The feedback is about answer length and should update output budget behavior.",
        ))
    if any(k in text for k in ["太短", "详细", "展开", "深入", "deep", "detail"]):
        targets.append((
            "context_budget.md",
            "Modes",
            f"For {domain_label}/{task_label}, allow deep mode when the user asks for detailed reasoning.",
            "The feedback is about depth and should update mode selection behavior.",
        ))
    if any(k in text for k in ["结构", "模板", "格式", "这个结构", "template", "format"]):
        targets.append((
            "task_patterns.md",
            domain_label if domain_label != "Global" else task_label,
            f"For {domain_label}/{task_label}, reuse the approved structure from feedback: {feedback}",
            "The feedback is about reusable structure and should update task patterns.",
        ))
    if any(k in text for k in ["以后", "下次", "默认", "总是", "记住", "preference", "remember"]):
        targets.append((
            "user_preferences.md",
            domain_label,
            f"For {domain_label}/{task_label}, follow this stable preference: {feedback}",
            "The feedback asks for future behavior and should update user preferences.",
        ))
    if not targets:
        targets.append((
            "feedback_log.md",
            "Feedback",
            feedback,
            "The feedback is useful history but not clearly stable enough for a permanent rule.",
        ))
    unique: list[tuple[str, str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in targets:
        key = (item[0], item[1], item[2])
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def proposal_to_markdown(proposal: Proposal) -> str:
    data = json.dumps(asdict(proposal), ensure_ascii=False, indent=2)
    return f"""# Feedback Evolution Proposal: {proposal.proposal_id}

```json
{data}
```

## Review

- Status: {proposal.status}
- Target: `knowledge/profile/{proposal.target_file}` -> `{proposal.target_section}`
- Proposed bullet: {proposal.bullet}

## Rationale

{proposal.rationale}
"""


def parse_proposal(path: Path) -> Proposal:
    text = read_text(path)
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Proposal JSON block not found: {path}")
    data = json.loads(match.group(1))
    return Proposal(**data)


def save_proposal(workspace: Path, proposal: Proposal) -> Path:
    path = proposals_dir(workspace) / f"{proposal.proposal_id}.md"
    write_text(path, proposal_to_markdown(proposal))
    return path


def record_feedback(workspace: Path, feedback: str, domain: str, task_type: str) -> None:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"- {now} | domain={domain or 'general'} | task={task_type or 'general'} | {feedback}"
    append_once(profile_dir(workspace) / "feedback_log.md", line)


def create_proposals(workspace: Path, feedback: str, domain: str, task_type: str) -> list[Proposal]:
    init(workspace, verbose=False)
    feedback = clean_feedback(feedback)
    record_feedback(workspace, feedback, domain, task_type)
    proposals: list[Proposal] = []
    created_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    for index, (target_file, target_section, bullet, rationale) in enumerate(infer_targets(feedback, domain, task_type), start=1):
        proposal_id = f"{timestamp}-{index}-{stable_hash(feedback + target_file + target_section)}"
        proposal = Proposal(
            proposal_id=proposal_id,
            created_at=created_at,
            feedback=feedback,
            domain=domain or "general",
            task_type=task_type or "general",
            target_file=target_file,
            target_section=target_section,
            bullet=bullet,
            rationale=rationale,
        )
        save_proposal(workspace, proposal)
        proposals.append(proposal)
    return proposals


def ensure_section(content: str, section: str) -> str:
    if section == "Feedback":
        return content
    heading = f"## {section}"
    if heading in content:
        return content
    if content and not content.endswith("\n"):
        content += "\n"
    return content + f"\n{heading}\n"


def append_to_section(path: Path, section: str, bullet: str) -> bool:
    content = read_text(path)
    line = bullet if bullet.startswith("- ") else f"- {bullet}"
    if line in content:
        return False
    content = ensure_section(content, section)
    if section == "Feedback":
        return append_once(path, line)

    heading = f"## {section}"
    lines = content.splitlines()
    output: list[str] = []
    inserted = False
    in_section = False
    for current in lines:
        if current.strip() == heading:
            in_section = True
            output.append(current)
            continue
        if in_section and current.startswith("## ") and current.strip() != heading:
            output.append(line)
            inserted = True
            in_section = False
        output.append(current)
    if in_section and not inserted:
        output.append(line)
        inserted = True
    if not inserted:
        output.append("")
        output.append(heading)
        output.append(line)
    write_text(path, "\n".join(output).rstrip() + "\n")
    return True


def mark_applied(path: Path, proposal: Proposal) -> None:
    proposal.status = "applied"
    write_text(path, proposal_to_markdown(proposal))


def apply_proposal(workspace: Path, proposal_id: str) -> None:
    init(workspace, verbose=False)
    path = proposals_dir(workspace) / f"{proposal_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"Proposal not found: {proposal_id}")
    proposal = parse_proposal(path)
    if proposal.status == "applied":
        print(f"Proposal already applied: {proposal_id}")
        return
    target = profile_dir(workspace) / proposal.target_file
    changed = append_to_section(target, proposal.target_section, proposal.bullet)
    evolution_line = (
        f"- {dt.date.today().isoformat()} | {proposal.proposal_id} | "
        f"`{proposal.target_file}`/{proposal.target_section}: {proposal.bullet}"
    )
    append_once(profile_dir(workspace) / "template_evolution.md", evolution_line)
    append_once(knowledge_dir(workspace) / "log.md", f"## [{dt.date.today().isoformat()}] maintain | applied feedback proposal {proposal.proposal_id}")
    mark_applied(path, proposal)
    print(f"Applied proposal: {proposal_id}")
    print(f"Changed target: {'yes' if changed else 'no, duplicate already present'}")


def list_proposals(workspace: Path, status: str) -> None:
    init(workspace, verbose=False)
    rows = []
    for path in sorted(proposals_dir(workspace).glob("*.md")):
        try:
            proposal = parse_proposal(path)
        except Exception:
            continue
        if status != "all" and proposal.status != status:
            continue
        rows.append(proposal)
    if not rows:
        print("No proposals.")
        return
    for proposal in rows:
        print(f"- {proposal.proposal_id} | {proposal.status} | {proposal.target_file}/{proposal.target_section} | {proposal.feedback}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Feedback template evolution manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("--workspace")

    p_propose = sub.add_parser("propose")
    p_propose.add_argument("--workspace")
    p_propose.add_argument("--feedback", required=True)
    p_propose.add_argument("--domain", default="general")
    p_propose.add_argument("--task-type", default="general")
    p_propose.add_argument("--format", choices=["markdown", "json"], default="markdown")

    p_list = sub.add_parser("list")
    p_list.add_argument("--workspace")
    p_list.add_argument("--status", choices=["pending", "applied", "all"], default="pending")

    p_apply = sub.add_parser("apply")
    p_apply.add_argument("--workspace")
    p_apply.add_argument("--proposal", required=True)

    args = parser.parse_args()
    workspace = workspace_path(getattr(args, "workspace", None))

    if args.cmd == "init":
        init(workspace)
    elif args.cmd == "propose":
        proposals = create_proposals(workspace, args.feedback, args.domain, args.task_type)
        if args.format == "json":
            print(json.dumps([asdict(proposal) for proposal in proposals], ensure_ascii=False, indent=2))
        else:
            print("\n\n".join(proposal_to_markdown(proposal) for proposal in proposals))
    elif args.cmd == "list":
        list_proposals(workspace, args.status)
    elif args.cmd == "apply":
        apply_proposal(workspace, args.proposal)


if __name__ == "__main__":
    main()
