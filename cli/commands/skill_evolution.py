"""Conservative skill evolution workflow.

The evolution flow intentionally keeps the live skill immutable until the user
explicitly applies a proposal:

1. suggest: inspect a skill and print improvement ideas.
2. draft: copy the skill into a proposal workspace for editing.
3. apply: validate the proposal copy, back up the live skill, then replace it.
4. rollback: restore a previous backup.
"""

from __future__ import annotations

import json
import os
import py_compile
import re
import shutil
import time
import uuid
import difflib
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from cli.utils import get_builtin_skills_dir, get_project_root, get_skills_dir, get_workspace_dir


_SAFE_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_\-]{0,63}$")
_TEXT_DIFF_EXTENSIONS = {
    ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".py", ".js", ".ts", ".tsx", ".jsx", ".css", ".html", ".xml",
}


class SkillEvolutionError(Exception):
    """Raised when a skill evolution operation cannot be completed."""


@dataclass
class ValidationResult:
    ok: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class DraftResult:
    proposal_id: str
    proposal_dir: str
    editable_skill_dir: str
    suggestions: List[str]
    evidence: Dict[str, object] = field(default_factory=dict)


@dataclass
class ApplyResult:
    skill_name: str
    proposal_id: str
    backup_id: str
    backup_dir: str
    target_dir: str
    warnings: List[str] = field(default_factory=list)


@dataclass
class RollbackResult:
    skill_name: str
    backup_id: str
    restored_from: str
    safety_backup_id: str
    target_dir: str


def _check_safe_name(value: str, label: str = "name") -> str:
    value = (value or "").strip()
    if not _SAFE_NAME_RE.match(value):
        raise SkillEvolutionError(
            f"Invalid {label} '{value}'. Use letters, digits, hyphens, and underscores."
        )
    return value


def _is_relative_to(path: str, root: str) -> bool:
    path = os.path.realpath(path)
    root = os.path.realpath(root)
    try:
        common = os.path.commonpath([path, root])
    except ValueError:
        return False
    return common == root


def _ensure_inside(path: str, root: str, label: str) -> str:
    path = os.path.realpath(path)
    root = os.path.realpath(root)
    if not _is_relative_to(path, root):
        raise SkillEvolutionError(f"{label} escapes expected root: {path}")
    return path


def get_evolution_root() -> str:
    return os.path.join(get_workspace_dir(), "skill_evolution")


def get_proposals_root() -> str:
    return os.path.join(get_evolution_root(), "proposals")


def get_versions_root() -> str:
    return os.path.join(get_skills_dir(), ".versions")


def get_events_path() -> str:
    return os.path.join(get_evolution_root(), "events.jsonl")


def record_event(action: str, skill_name: str = "", proposal_id: str = "", status: str = "success", **details) -> Dict[str, object]:
    event = {
        "event_id": time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8],
        "created_at": int(time.time()),
        "action": str(action or ""),
        "status": str(status or "success"),
        "skill_name": str(skill_name or ""),
        "proposal_id": str(proposal_id or ""),
        "details": details,
    }
    path = get_events_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return event


def query_events(
    limit: int = 100,
    offset: int = 0,
    start_at: Optional[int] = None,
    end_at: Optional[int] = None,
) -> Dict[str, object]:
    limit = max(1, min(int(limit or 100), 500))
    offset = max(0, int(offset or 0))
    path = get_events_path()
    if not os.path.isfile(path):
        return {"events": [], "total": 0, "limit": limit, "offset": offset}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception:
        return {"events": [], "total": 0, "limit": limit, "offset": offset}
    events = []
    for line in reversed(lines):
        try:
            event = json.loads(line)
        except Exception:
            continue
        created_at = int(event.get("created_at") or 0)
        if start_at is not None and created_at < int(start_at):
            continue
        if end_at is not None and created_at > int(end_at):
            continue
        events.append(event)
    total = len(events)
    return {
        "events": events[offset:offset + limit],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def list_events(
    limit: int = 100,
    offset: int = 0,
    start_at: Optional[int] = None,
    end_at: Optional[int] = None,
) -> List[Dict[str, object]]:
    return query_events(limit=limit, offset=offset, start_at=start_at, end_at=end_at)["events"]


def resolve_skill_dir(name: str, include_builtin: bool = True) -> str:
    name = _check_safe_name(name, "skill name")
    candidates = [os.path.join(get_skills_dir(), name)]
    if include_builtin:
        candidates.append(os.path.join(get_builtin_skills_dir(), name))

    for candidate in candidates:
        if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, "SKILL.md")):
            return candidate

    raise SkillEvolutionError(f"Skill '{name}' was not found.")


def _parse_frontmatter(content: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return result
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        result[key.strip()] = val.strip().strip('"').strip("'")
    return result


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def _ignore_for_copy(_dir: str, names: List[str]) -> List[str]:
    ignored = []
    for name in names:
        if name in {"__pycache__", ".git", ".pytest_cache"}:
            ignored.append(name)
        elif name.endswith((".pyc", ".pyo")):
            ignored.append(name)
    return ignored


def collect_skill_suggestions(name: str) -> List[str]:
    skill_dir = resolve_skill_dir(name, include_builtin=True)
    skill_md = os.path.join(skill_dir, "SKILL.md")
    content = _read_text(skill_md)
    frontmatter = _parse_frontmatter(content)
    lower = content.lower()

    suggestions: List[str] = []
    desc = frontmatter.get("description", "").strip()
    if len(desc) < 40:
        suggestions.append("Expand the frontmatter description with clear trigger conditions.")
    if "when to use" not in lower and "use when" not in lower:
        suggestions.append("Add a 'When to use' section so the agent invokes the skill at the right time.")
    if "input" not in lower and "parameter" not in lower:
        suggestions.append("Document expected inputs and required parameters.")
    if "output" not in lower and "return" not in lower:
        suggestions.append("Document the expected output shape or final answer style.")
    if "error" not in lower and "fail" not in lower and "fallback" not in lower:
        suggestions.append("Add failure handling guidance and fallback behavior.")
    if "secret" not in lower and "token" not in lower and "api key" not in lower:
        suggestions.append("State whether the skill needs credentials and how to keep them out of prompts/logs.")

    scripts_dir = os.path.join(skill_dir, "scripts")
    if os.path.isdir(scripts_dir):
        py_files = [
            os.path.join(root, file_name)
            for root, _, files in os.walk(scripts_dir)
            for file_name in files
            if file_name.endswith(".py")
        ]
        if py_files and not any("test" in os.path.basename(p).lower() for p in py_files):
            suggestions.append("Add one small script-level smoke test or documented manual test case.")
    else:
        suggestions.append("If the skill calls external services, consider moving logic into scripts/ for easier testing.")

    recent = _recent_log_lines(name, max_lines=20)
    if recent:
        suggestions.append("Review recent run.log lines mentioning this skill; include recurring failures in the proposal.")

    if not suggestions:
        suggestions.append("No obvious structural issues found. Consider adding examples from real usage before changing behavior.")
    return suggestions


def _recent_log_lines(name: str, max_lines: int = 50) -> List[str]:
    from common.runtime import get_runtime_path
    log_path = get_runtime_path("logs", "run.log")
    if not os.path.isfile(log_path):
        return []
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception:
        return []
    needle = name.lower()
    hits = [line.strip() for line in lines if needle in line.lower()]
    return hits[-max_lines:]


def _load_skill_usage_logs(limit: int = 200) -> List[Dict[str, object]]:
    try:
        from common.quota import get_quota_manager

        return get_quota_manager().skill_usage_logs(limit=limit)
    except Exception:
        return []


def analyze_skill_usage(name: str, limit: int = 200) -> Dict[str, object]:
    name = _check_safe_name(name, "skill name")
    logs = _load_skill_usage_logs(limit=limit)
    needle = name.lower()
    matched = []
    for row in logs:
        tool_name = str(row.get("tool_name") or "").lower()
        text = " ".join(
            str(row.get(key) or "")
            for key in ("user_message", "arguments", "result", "status")
        ).lower()
        if tool_name == needle or needle in text:
            matched.append(row)

    failures = [
        row for row in matched
        if str(row.get("status") or "").lower() not in {"", "success", "ok", "done", "completed"}
    ]
    slow = [
        row for row in matched
        if float(row.get("execution_time") or 0) >= 10
    ]
    prompts = _top_samples([str(row.get("user_message") or "") for row in matched], max_items=5)
    errors = _top_samples(
        [
            str(row.get("result") or row.get("status") or "")
            for row in failures
            if str(row.get("result") or row.get("status") or "").strip()
        ],
        max_items=5,
    )

    signals = []
    if matched:
        signals.append(f"Recent matching runs: {len(matched)}")
    if failures:
        signals.append(f"Runs needing failure guidance: {len(failures)}")
    if slow:
        signals.append(f"Slow runs (>=10s): {len(slow)}")
    if not matched:
        signals.append("No recent usage records matched this skill; changes are based on structural analysis.")

    return {
        "skill_name": name,
        "sample_size": len(logs),
        "matched_count": len(matched),
        "failure_count": len(failures),
        "slow_count": len(slow),
        "signals": signals,
        "sample_prompts": prompts,
        "sample_errors": errors,
        "generated_at": int(time.time()),
    }


def score_skills(skill_names: Optional[List[str]] = None, limit: int = 500) -> List[Dict[str, object]]:
    logs = _load_skill_usage_logs(limit=limit)
    names = []
    if skill_names:
        for name in skill_names:
            try:
                names.append(_check_safe_name(str(name), "skill name"))
            except SkillEvolutionError:
                continue
    else:
        names = sorted({
            str(row.get("tool_name") or "").strip()
            for row in logs
            if str(row.get("tool_name") or "").strip()
        })

    grouped: Dict[str, List[Dict[str, object]]] = {name: [] for name in names}
    for row in logs:
        tool_name = str(row.get("tool_name") or "").strip()
        if tool_name in grouped:
            grouped[tool_name].append(row)

    rows = []
    for name in names:
        skill_logs = grouped.get(name, [])
        total = len(skill_logs)
        failures = [
            row for row in skill_logs
            if _is_failure_status(str(row.get("status") or ""))
        ]
        slow = [
            row for row in skill_logs
            if float(row.get("execution_time") or 0) >= 10
        ]
        total_time = sum(float(row.get("execution_time") or 0) for row in skill_logs)
        avg_time = round(total_time / total, 2) if total else 0.0
        failure_rate = (len(failures) / total) if total else 0.0
        slow_rate = (len(slow) / total) if total else 0.0
        score = 100
        score -= int(round(failure_rate * 55))
        score -= int(round(slow_rate * 20))
        score -= min(15, int(avg_time // 3))
        if total == 0:
            score = 100
        score = max(0, min(100, score))
        priority = "none"
        if total > 0 and score < 60:
            priority = "high"
        elif total > 0 and score < 80:
            priority = "medium"
        rows.append({
            "skill_name": name,
            "score": score,
            "priority": priority,
            "calls": total,
            "successes": total - len(failures),
            "failures": len(failures),
            "slow_runs": len(slow),
            "avg_time": avg_time,
            "failure_rate": round(failure_rate, 3),
            "slow_rate": round(slow_rate, 3),
            "last_used": max([int(row.get("created_at") or 0) for row in skill_logs], default=0),
        })
    return sorted(rows, key=lambda item: (item["score"], -item["calls"], item["skill_name"]))


def create_auto_learn_queue(
    skill_names: Optional[List[str]] = None,
    max_items: int = 3,
    priorities: Optional[List[str]] = None,
) -> Dict[str, object]:
    max_items = max(1, min(int(max_items or 3), 10))
    priorities = priorities or ["high", "medium"]
    allowed = {str(item).lower() for item in priorities}
    created = []
    skipped = []
    for score in score_skills(skill_names):
        name = str(score.get("skill_name") or "")
        if score.get("priority") not in allowed:
            continue
        pending = _pending_auto_proposal_for_skill(name)
        if pending:
            skipped.append({
                "skill_name": name,
                "reason": "pending_auto_proposal",
                "proposal_id": pending.get("proposal_id"),
                "score": score,
            })
            continue
        if len(created) >= max_items:
            break
        try:
            draft = create_auto_learn_proposal(name)
            created.append({
                "skill_name": name,
                "proposal_id": draft.proposal_id,
                "proposal_dir": draft.proposal_dir,
                "score": score,
            })
        except Exception as e:
            skipped.append({
                "skill_name": name,
                "reason": str(e),
                "score": score,
            })
    result = {
        "created": created,
        "skipped": skipped,
        "max_items": max_items,
    }
    record_event(
        "auto_queue_completed",
        status="success",
        created_count=len(created),
        skipped_count=len(skipped),
        max_items=max_items,
        created=[{"skill_name": item.get("skill_name"), "proposal_id": item.get("proposal_id")} for item in created],
        skipped=[{"skill_name": item.get("skill_name"), "reason": item.get("reason")} for item in skipped],
    )
    return result


def _pending_auto_proposal_for_skill(name: str) -> Optional[Dict[str, object]]:
    for proposal in list_proposals(name):
        status = str(proposal.get("status") or "")
        mode = str(proposal.get("mode") or "")
        if mode == "auto_learn" and status not in {"applied", "rejected"}:
            return proposal
    return None


def _is_failure_status(status: str) -> bool:
    normalized = str(status or "").strip().lower()
    return normalized not in {"", "success", "ok", "done", "completed"}


def _top_samples(values: List[str], max_items: int = 5, max_chars: int = 220) -> List[str]:
    samples = []
    seen = set()
    for value in values:
        text = " ".join(str(value or "").split())
        if not text:
            continue
        if len(text) > max_chars:
            text = text[:max_chars].rstrip() + "..."
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        samples.append(text)
        if len(samples) >= max_items:
            break
    return samples


def format_suggestions(name: str) -> str:
    suggestions = collect_skill_suggestions(name)
    skill_dir = resolve_skill_dir(name, include_builtin=True)
    lines = [
        f"Skill evolution suggestions: {name}",
        "",
        f"Skill path: {skill_dir}",
        "",
    ]
    for idx, item in enumerate(suggestions, 1):
        lines.append(f"{idx}. {item}")
    lines.extend([
        "",
        "Next:",
        f"  zv skill evolve draft {name}",
        "  Edit the proposal's skill/ copy, then apply it after review.",
    ])
    return "\n".join(lines)


def create_draft(name: str) -> DraftResult:
    name = _check_safe_name(name, "skill name")
    source_dir = resolve_skill_dir(name, include_builtin=True)
    proposals_root = get_proposals_root()
    proposal_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    proposal_dir = os.path.join(proposals_root, name, proposal_id)
    proposal_dir = _ensure_inside(proposal_dir, proposals_root, "proposal directory")
    editable_skill_dir = os.path.join(proposal_dir, "skill")

    if os.path.exists(proposal_dir):
        raise SkillEvolutionError(f"Proposal already exists: {proposal_id}")

    os.makedirs(proposal_dir, exist_ok=False)
    shutil.copytree(source_dir, editable_skill_dir, ignore=_ignore_for_copy)

    suggestions = collect_skill_suggestions(name)
    metadata = {
        "proposal_id": proposal_id,
        "skill_name": name,
        "source_dir": source_dir,
        "editable_skill_dir": editable_skill_dir,
        "created_at": int(time.time()),
        "status": "draft",
    }
    _write_text(os.path.join(proposal_dir, "proposal.json"), json.dumps(metadata, indent=2))
    _write_text(os.path.join(proposal_dir, "proposal.md"), _build_proposal_markdown(name, proposal_id, suggestions))

    result = DraftResult(
        proposal_id=proposal_id,
        proposal_dir=proposal_dir,
        editable_skill_dir=editable_skill_dir,
        suggestions=suggestions,
    )
    record_event(
        "draft_created",
        skill_name=name,
        proposal_id=proposal_id,
        proposal_dir=proposal_dir,
        suggestions_count=len(suggestions),
    )
    return result


def create_auto_learn_proposal(name: str) -> DraftResult:
    name = _check_safe_name(name, "skill name")
    draft = create_draft(name)
    evidence = analyze_skill_usage(name)
    skill_md = os.path.join(draft.editable_skill_dir, "SKILL.md")
    content = _read_text(skill_md)
    updated = _apply_auto_learning_notes(content, name, draft.suggestions, evidence)
    _write_text(skill_md, updated)
    _write_text(
        os.path.join(draft.proposal_dir, "evidence.json"),
        json.dumps(evidence, indent=2, ensure_ascii=False),
    )

    metadata = _load_proposal_metadata(draft.proposal_dir)
    metadata.update({
        "status": "auto_learned",
        "mode": "auto_learn",
        "evidence_path": os.path.join(draft.proposal_dir, "evidence.json"),
        "evidence_summary": {
            "matched_count": evidence.get("matched_count", 0),
            "failure_count": evidence.get("failure_count", 0),
            "slow_count": evidence.get("slow_count", 0),
        },
    })
    _save_proposal_metadata(draft.proposal_dir, metadata)
    _write_text(
        os.path.join(draft.proposal_dir, "proposal.md"),
        _build_auto_proposal_markdown(name, draft.proposal_id, draft.suggestions, evidence),
    )
    draft.evidence = evidence
    record_event(
        "auto_learn_created",
        skill_name=name,
        proposal_id=draft.proposal_id,
        proposal_dir=draft.proposal_dir,
        evidence_summary=metadata.get("evidence_summary", {}),
    )
    return draft


def _apply_auto_learning_notes(
    content: str,
    name: str,
    suggestions: List[str],
    evidence: Dict[str, object],
) -> str:
    section = _build_auto_learning_section(name, suggestions, evidence)
    pattern = re.compile(
        r"\n## Auto-Learned Usage Notes\n.*?(?=\n## |\Z)",
        re.DOTALL,
    )
    if pattern.search(content):
        return pattern.sub("\n" + section.rstrip() + "\n", content)
    return content.rstrip() + "\n\n" + section


def _build_auto_learning_section(
    name: str,
    suggestions: List[str],
    evidence: Dict[str, object],
) -> str:
    lines = [
        "## Auto-Learned Usage Notes",
        "",
        "Generated by the skill evolution workflow from recent usage logs and structural checks.",
        "",
        "### Invocation Signals",
    ]
    signals = evidence.get("signals") or []
    for signal in signals:
        lines.append(f"- {signal}")
    if not signals:
        lines.append(f"- Use this skill when the user request clearly matches `{name}`.")

    prompts = evidence.get("sample_prompts") or []
    if prompts:
        lines.extend(["", "### Recent User Requests"])
        for prompt in prompts:
            lines.append(f"- {prompt}")

    lines.extend(["", "### Improvement Guidance"])
    for item in suggestions:
        lines.append(f"- {item}")

    errors = evidence.get("sample_errors") or []
    lines.extend(["", "### Failure Handling"])
    if errors:
        for item in errors:
            lines.append(f"- If a similar failure appears, explain the limitation and provide a concrete fallback: {item}")
    else:
        lines.append("- If required inputs, credentials, files, or network access are missing, ask for the missing item or choose a documented fallback.")
    lines.append("- Keep outputs concise, verifiable, and aligned with the user's requested format.")
    lines.append("")
    return "\n".join(lines)


def _build_auto_proposal_markdown(
    name: str,
    proposal_id: str,
    suggestions: List[str],
    evidence: Dict[str, object],
) -> str:
    lines = [
        f"# Auto-Learned Skill Proposal: {name}",
        "",
        f"Proposal ID: `{proposal_id}`",
        "",
        "## Evidence",
        "",
        f"- Recent logs scanned: {evidence.get('sample_size', 0)}",
        f"- Matching skill runs: {evidence.get('matched_count', 0)}",
        f"- Failure-like runs: {evidence.get('failure_count', 0)}",
        f"- Slow runs: {evidence.get('slow_count', 0)}",
        "",
        "## Automated Changes",
        "",
        "- Added or refreshed `## Auto-Learned Usage Notes` in `skill/SKILL.md`.",
        "- Wrote evidence details to `evidence.json`.",
        "",
        "## Suggested Improvements",
        "",
    ]
    for item in suggestions:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Validation",
        "",
        "- [ ] Validate passes in the Skill Evolution UI.",
        "- [ ] Review `skill/SKILL.md` before applying.",
        "",
        "## Rollback",
        "",
        "Use the generated backup if this proposal makes behavior worse.",
        "",
    ])
    return "\n".join(lines)


def _build_proposal_markdown(name: str, proposal_id: str, suggestions: List[str]) -> str:
    lines = [
        f"# Skill Evolution Proposal: {name}",
        "",
        f"Proposal ID: `{proposal_id}`",
        "",
        "## Intent",
        "",
        "- Describe the user-facing problem this proposal fixes.",
        "- Note which files in `skill/` were changed.",
        "",
        "## Suggested Improvements",
        "",
    ]
    for item in suggestions:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Validation",
        "",
        "- [ ] `zv skill evolve apply <proposal_id> --yes` validation passes.",
        "- [ ] Manual prompt tested in chat.",
        "",
        "## Rollback",
        "",
        "Use `zv skill evolve rollback <skill-name>` to restore the latest backup.",
        "",
    ])
    return "\n".join(lines)


def replay_proposal(proposal_id: str) -> Dict[str, object]:
    proposal_dir = _find_proposal(proposal_id)
    metadata = _load_proposal_metadata(proposal_dir)
    skill_name = _check_safe_name(metadata.get("skill_name", ""), "skill name")
    editable_skill_dir = _ensure_inside(os.path.join(proposal_dir, "skill"), proposal_dir, "editable skill directory")
    skill_md = os.path.join(editable_skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        raise SkillEvolutionError("Proposal is missing skill/SKILL.md")

    content = _read_text(skill_md)
    lower = content.lower()
    evidence = _load_proposal_evidence(proposal_dir) or analyze_skill_usage(skill_name)
    checks = []

    _add_replay_check(
        checks,
        "invocation-guidance",
        "Invocation guidance",
        ("when to use" in lower or "use when" in lower or "invocation signals" in lower),
        "Skill instructions include when the agent should use the skill.",
        "Add a clear 'When to use' section or invocation signals.",
    )
    _add_replay_check(
        checks,
        "input-guidance",
        "Input guidance",
        ("input" in lower or "parameter" in lower or "required" in lower),
        "Skill instructions describe inputs, parameters, or required data.",
        "Document expected inputs and required parameters.",
    )
    _add_replay_check(
        checks,
        "output-guidance",
        "Output guidance",
        ("output" in lower or "return" in lower or "final answer" in lower or "format" in lower),
        "Skill instructions describe output shape or response format.",
        "Document expected output shape or final answer style.",
    )
    _add_replay_check(
        checks,
        "fallback-guidance",
        "Fallback guidance",
        ("fallback" in lower or "fail" in lower or "error" in lower or "missing" in lower),
        "Skill instructions include failure handling or fallback guidance.",
        "Add guidance for errors, missing inputs, unavailable files, or network failures.",
    )

    prompts = evidence.get("sample_prompts") or []
    errors = evidence.get("sample_errors") or []
    for idx, prompt in enumerate(prompts[:3], 1):
        tokens = _meaningful_tokens(prompt)
        covered = _token_coverage(tokens, lower) >= 0.25 if tokens else True
        _add_replay_check(
            checks,
            f"history-prompt-{idx}",
            f"Historical request {idx}",
            covered,
            f"Proposal mentions enough context from: {prompt}",
            f"Historical request may not be reflected yet: {prompt}",
            warning_only=True,
        )
    for idx, error in enumerate(errors[:3], 1):
        tokens = _meaningful_tokens(error)
        covered = any(token in lower for token in tokens) or "fallback" in lower or "failure handling" in lower
        _add_replay_check(
            checks,
            f"history-error-{idx}",
            f"Historical failure {idx}",
            covered,
            f"Proposal covers failure signal: {error}",
            f"Failure signal may not be covered: {error}",
            warning_only=True,
        )

    passed = [c for c in checks if c["status"] == "passed"]
    warnings = [c for c in checks if c["status"] == "warning"]
    failed = [c for c in checks if c["status"] == "failed"]
    result = {
        "proposal_id": proposal_id,
        "skill_name": skill_name,
        "summary": {
            "passed": len(passed),
            "warnings": len(warnings),
            "failed": len(failed),
            "total": len(checks),
        },
        "checks": checks,
        "evidence_summary": {
            "matched_count": evidence.get("matched_count", 0),
            "failure_count": evidence.get("failure_count", 0),
            "slow_count": evidence.get("slow_count", 0),
        },
    }
    metadata["last_replay"] = {
        "checked_at": int(time.time()),
        "summary": result["summary"],
    }
    _save_proposal_metadata(proposal_dir, metadata)
    record_event(
        "replay_checked",
        skill_name=skill_name,
        proposal_id=proposal_id,
        status="failed" if result["summary"]["failed"] else "success",
        summary=result["summary"],
    )
    return result


def ai_rewrite_proposal(proposal_id: str, llm_callable=None) -> Dict[str, object]:
    proposal_dir = _find_proposal(proposal_id)
    metadata = _load_proposal_metadata(proposal_dir)
    skill_name = _check_safe_name(metadata.get("skill_name", ""), "skill name")
    editable_skill_dir = _ensure_inside(os.path.join(proposal_dir, "skill"), proposal_dir, "editable skill directory")
    skill_md = os.path.join(editable_skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        raise SkillEvolutionError("Proposal is missing skill/SKILL.md")

    original = _read_text(skill_md)
    evidence = _load_proposal_evidence(proposal_dir) or analyze_skill_usage(skill_name)
    replay = replay_proposal(proposal_id)
    prompt = _build_ai_rewrite_prompt(skill_name, original, evidence, replay)
    rewritten = _call_rewrite_llm(prompt, llm_callable=llm_callable)
    rewritten = _extract_rewritten_skill_md(rewritten)
    _validate_rewritten_skill_md(rewritten, skill_name)

    backup_path = _backup_proposal_skill_md(proposal_dir, original)
    _write_text(skill_md, rewritten.rstrip() + "\n")

    validation = validate_skill_dir(editable_skill_dir)
    replay_after = replay_proposal(proposal_id)
    metadata = _load_proposal_metadata(proposal_dir)
    metadata.update({
        "status": "ai_rewritten",
        "mode": metadata.get("mode") or "ai_rewrite",
        "last_ai_rewrite": {
            "rewritten_at": int(time.time()),
            "backup_path": backup_path,
            "validation": {
                "ok": validation.ok,
                "errors": validation.errors,
                "warnings": validation.warnings,
            },
            "replay_summary": replay_after.get("summary", {}),
        },
    })
    _save_proposal_metadata(proposal_dir, metadata)
    result = {
        "proposal_id": proposal_id,
        "skill_name": skill_name,
        "backup_path": backup_path,
        "validation": {
            "ok": validation.ok,
            "errors": validation.errors,
            "warnings": validation.warnings,
        },
        "replay": replay_after,
    }
    record_event(
        "ai_rewrite_completed",
        skill_name=skill_name,
        proposal_id=proposal_id,
        status="success" if validation.ok else "failed",
        backup_path=backup_path,
        validation=result["validation"],
        replay_summary=replay_after.get("summary", {}),
    )
    return result


def evaluate_safe_apply(proposal_id: str) -> Dict[str, object]:
    proposal_dir = _find_proposal(proposal_id)
    metadata = _load_proposal_metadata(proposal_dir)
    skill_name = _check_safe_name(metadata.get("skill_name", ""), "skill name")
    reasons = []
    warnings = []

    status = str(metadata.get("status") or "")
    mode = str(metadata.get("mode") or "")
    if mode != "auto_learn" and status not in {"auto_learned", "ai_rewritten"}:
        reasons.append("proposal is not an auto-learn or AI-rewritten proposal")
    if status == "applied":
        reasons.append("proposal is already applied")

    diff = get_proposal_diff(proposal_id)
    changed_files = [item.get("path") for item in diff.get("files", [])]
    if changed_files != ["SKILL.md"]:
        reasons.append("safe auto-apply only allows a single SKILL.md change")

    validation = validate_skill_dir(os.path.join(proposal_dir, "skill"))
    if not validation.ok:
        reasons.append("validation failed")

    replay = replay_proposal(proposal_id)
    if int(replay.get("summary", {}).get("failed", 0) or 0) > 0:
        reasons.append("replay has failed checks")
    if int(replay.get("summary", {}).get("warnings", 0) or 0) > 0:
        warnings.append("replay has warnings")

    target_dir = os.path.join(get_skills_dir(), skill_name)
    if not os.path.isdir(target_dir):
        reasons.append("live custom skill was not found")

    return {
        "proposal_id": proposal_id,
        "skill_name": skill_name,
        "safe": not reasons,
        "reasons": reasons,
        "warnings": warnings,
        "changed_files": changed_files,
        "validation": {
            "ok": validation.ok,
            "errors": validation.errors,
            "warnings": validation.warnings,
        },
        "replay": replay,
    }


def auto_apply_safe(max_items: int = 3) -> Dict[str, object]:
    max_items = max(1, min(int(max_items or 3), 10))
    applied = []
    skipped = []
    for proposal in list_proposals():
        if len(applied) >= max_items:
            break
        proposal_id = proposal.get("proposal_id", "")
        try:
            evaluation = evaluate_safe_apply(proposal_id)
            if not evaluation["safe"]:
                skipped.append({
                    "proposal_id": proposal_id,
                    "skill_name": evaluation.get("skill_name"),
                    "reasons": evaluation.get("reasons", []),
                })
                continue
            result = apply_proposal(proposal_id)
            applied.append({
                "proposal_id": proposal_id,
                "skill_name": result.skill_name,
                "backup_id": result.backup_id,
                "backup_dir": result.backup_dir,
                "warnings": evaluation.get("warnings", []),
            })
        except Exception as e:
            skipped.append({
                "proposal_id": proposal_id,
                "skill_name": proposal.get("skill_name"),
                "reasons": [str(e)],
            })
    result = {
        "applied": applied,
        "skipped": skipped,
        "max_items": max_items,
    }
    record_event(
        "auto_apply_safe_completed",
        status="success",
        applied_count=len(applied),
        skipped_count=len(skipped),
        applied=[{"skill_name": item.get("skill_name"), "proposal_id": item.get("proposal_id"), "backup_id": item.get("backup_id")} for item in applied],
        skipped=[{"skill_name": item.get("skill_name"), "proposal_id": item.get("proposal_id"), "reasons": item.get("reasons")} for item in skipped],
    )
    return result


def run_evolution_cycle(
    skill_names: Optional[List[str]] = None,
    max_queue: int = 3,
    max_apply: int = 3,
    enable_ai_rewrite: bool = True,
    llm_callable=None,
) -> Dict[str, object]:
    scores = score_skills(skill_names)
    queue = create_auto_learn_queue(skill_names, max_items=max_queue)
    rewrites = []
    replays = []
    validations = []

    for item in queue.get("created", []):
        proposal_id = item.get("proposal_id", "")
        if not proposal_id:
            continue
        if enable_ai_rewrite:
            try:
                rewritten = ai_rewrite_proposal(proposal_id, llm_callable=llm_callable)
                rewrites.append({
                    "proposal_id": proposal_id,
                    "skill_name": rewritten.get("skill_name"),
                    "ok": bool(rewritten.get("validation", {}).get("ok")),
                    "backup_path": rewritten.get("backup_path"),
                    "replay_summary": rewritten.get("replay", {}).get("summary", {}),
                })
            except Exception as e:
                rewrites.append({
                    "proposal_id": proposal_id,
                    "skill_name": item.get("skill_name"),
                    "ok": False,
                    "error": str(e),
                })

        try:
            replay = replay_proposal(proposal_id)
            replays.append({
                "proposal_id": proposal_id,
                "skill_name": replay.get("skill_name"),
                "summary": replay.get("summary", {}),
            })
        except Exception as e:
            replays.append({
                "proposal_id": proposal_id,
                "skill_name": item.get("skill_name"),
                "error": str(e),
            })

        try:
            proposal_dir = _find_proposal(proposal_id)
            validation = validate_skill_dir(os.path.join(proposal_dir, "skill"))
            validations.append({
                "proposal_id": proposal_id,
                "skill_name": item.get("skill_name"),
                "ok": validation.ok,
                "errors": validation.errors,
                "warnings": validation.warnings,
            })
        except Exception as e:
            validations.append({
                "proposal_id": proposal_id,
                "skill_name": item.get("skill_name"),
                "ok": False,
                "errors": [str(e)],
                "warnings": [],
            })

    applied = auto_apply_safe(max_items=max_apply)
    result = {
        "scores": scores,
        "queue": queue,
        "rewrites": rewrites,
        "replays": replays,
        "validations": validations,
        "auto_apply": applied,
        "summary": {
            "queued": len(queue.get("created", [])),
            "queue_skipped": len(queue.get("skipped", [])),
            "rewritten": len([item for item in rewrites if item.get("ok")]),
            "rewrite_failed": len([item for item in rewrites if not item.get("ok")]),
            "applied": len(applied.get("applied", [])),
            "apply_skipped": len(applied.get("skipped", [])),
        },
    }
    record_event(
        "cycle_completed",
        status="success",
        summary=result["summary"],
        queued=[{"skill_name": item.get("skill_name"), "proposal_id": item.get("proposal_id")} for item in queue.get("created", [])],
        applied=[{"skill_name": item.get("skill_name"), "proposal_id": item.get("proposal_id"), "backup_id": item.get("backup_id")} for item in applied.get("applied", [])],
    )
    return result


def _build_ai_rewrite_prompt(
    skill_name: str,
    skill_md: str,
    evidence: Dict[str, object],
    replay: Dict[str, object],
) -> str:
    evidence_text = json.dumps(evidence, ensure_ascii=False, indent=2)[:6000]
    replay_text = json.dumps(replay, ensure_ascii=False, indent=2)[:6000]
    return (
        "You are improving a ZVAgent skill instruction file.\n"
        "Rewrite the SKILL.md so the agent invokes and executes this skill more reliably.\n"
        "Rules:\n"
        "- Return ONLY the complete rewritten SKILL.md content.\n"
        "- Preserve valid YAML frontmatter, including the original skill name.\n"
        "- Do not invent credentials, APIs, files, or capabilities not implied by the skill.\n"
        "- Keep any existing script references or operational steps that are still useful.\n"
        "- Improve trigger conditions, expected inputs, output style, and fallback behavior.\n"
        "- Incorporate historical evidence and replay warnings.\n\n"
        f"Skill name: {skill_name}\n\n"
        f"Current SKILL.md:\n{skill_md[:12000]}\n\n"
        f"Evidence JSON:\n{evidence_text}\n\n"
        f"Replay JSON:\n{replay_text}\n"
    )


def _call_rewrite_llm(prompt: str, llm_callable=None) -> str:
    if llm_callable:
        return str(llm_callable(prompt) or "")
    try:
        from bridge.bridge import Bridge
        from models.session_manager import Session

        bot = Bridge().get_bot("chat")
        session = Session("__skill_ai_rewrite__", system_prompt="")
        session.messages = [{"role": "user", "content": prompt}]
        result = bot.reply_text(session) or {}
        content = (result.get("content") or "").strip()
        if not content or (result.get("completion_tokens", 1) or 0) <= 0:
            raise SkillEvolutionError(content or "LLM returned an empty rewrite.")
        return content
    except SkillEvolutionError:
        raise
    except Exception as e:
        raise SkillEvolutionError(f"AI rewrite failed: {e}")


def _extract_rewritten_skill_md(text: str) -> str:
    text = str(text or "").strip()
    fence = re.search(r"```(?:markdown|md)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    return text


def _validate_rewritten_skill_md(content: str, skill_name: str) -> None:
    if not content.strip():
        raise SkillEvolutionError("AI rewrite returned empty SKILL.md content.")
    frontmatter = _parse_frontmatter(content)
    if not frontmatter.get("name"):
        raise SkillEvolutionError("AI rewrite must preserve SKILL.md frontmatter with a name.")
    if frontmatter.get("name") != skill_name:
        raise SkillEvolutionError(
            f"AI rewrite changed skill name from '{skill_name}' to '{frontmatter.get('name')}'."
        )


def _backup_proposal_skill_md(proposal_dir: str, content: str) -> str:
    backup_dir = _ensure_inside(os.path.join(proposal_dir, "rewrite_backups"), proposal_dir, "rewrite backup directory")
    backup_path = os.path.join(backup_dir, time.strftime("SKILL-%Y%m%d-%H%M%S") + f"-{uuid.uuid4().hex[:6]}.md")
    _write_text(backup_path, content)
    return backup_path


def _load_proposal_evidence(proposal_dir: str) -> Dict[str, object]:
    path = os.path.join(proposal_dir, "evidence.json")
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _add_replay_check(
    checks: List[Dict[str, object]],
    check_id: str,
    title: str,
    ok: bool,
    passed_message: str,
    failed_message: str,
    warning_only: bool = False,
) -> None:
    if ok:
        status = "passed"
        message = passed_message
    else:
        status = "warning" if warning_only else "failed"
        message = failed_message
    checks.append({
        "id": check_id,
        "title": title,
        "status": status,
        "message": message,
    })


def _meaningful_tokens(text: str) -> List[str]:
    tokens = re.findall(r"[a-zA-Z0-9_\-]{4,}", str(text or "").lower())
    stop = {
        "this", "that", "with", "from", "please", "using", "skill",
        "failed", "failure", "error", "missing", "required",
    }
    return [token for token in tokens if token not in stop][:12]


def _token_coverage(tokens: List[str], lower_content: str) -> float:
    if not tokens:
        return 1.0
    hits = sum(1 for token in tokens if token in lower_content)
    return hits / len(tokens)


def list_proposals(name: Optional[str] = None) -> List[Dict[str, str]]:
    proposals_root = get_proposals_root()
    if not os.path.isdir(proposals_root):
        return []

    skill_names = [name] if name else sorted(os.listdir(proposals_root))
    rows: List[Dict[str, str]] = []
    for skill_name in skill_names:
        if not skill_name or skill_name.startswith("."):
            continue
        try:
            _check_safe_name(skill_name, "skill name")
        except SkillEvolutionError:
            continue
        skill_root = os.path.join(proposals_root, skill_name)
        if not os.path.isdir(skill_root):
            continue
        for proposal_id in sorted(os.listdir(skill_root), reverse=True):
            proposal_dir = os.path.join(skill_root, proposal_id)
            meta = _load_proposal_metadata(proposal_dir)
            rows.append({
                "skill_name": meta.get("skill_name", skill_name),
                "proposal_id": meta.get("proposal_id", proposal_id),
                "status": meta.get("status", "unknown"),
                "mode": meta.get("mode", "manual"),
                "evidence_summary": meta.get("evidence_summary", {}),
                "last_replay": meta.get("last_replay", {}),
                "last_ai_rewrite": meta.get("last_ai_rewrite", {}),
                "path": proposal_dir,
            })
    return rows


def get_proposal_diff(proposal_id: str, max_file_chars: int = 120000) -> Dict[str, object]:
    proposal_dir = _find_proposal(proposal_id)
    metadata = _load_proposal_metadata(proposal_dir)
    skill_name = _check_safe_name(metadata.get("skill_name", ""), "skill name")
    source_dir = metadata.get("source_dir") or resolve_skill_dir(skill_name, include_builtin=True)
    source_dir = os.path.realpath(source_dir)
    editable_dir = _ensure_inside(os.path.join(proposal_dir, "skill"), proposal_dir, "editable skill directory")
    if not os.path.isdir(editable_dir):
        raise SkillEvolutionError(f"Proposal skill directory was not found: {editable_dir}")

    files = []
    source_files = _collect_diffable_files(source_dir)
    edited_files = _collect_diffable_files(editable_dir)
    all_rel_paths = sorted(set(source_files) | set(edited_files))
    for rel_path in all_rel_paths:
        before_path = source_files.get(rel_path)
        after_path = edited_files.get(rel_path)
        before = _read_diff_text(before_path, max_file_chars) if before_path else ""
        after = _read_diff_text(after_path, max_file_chars) if after_path else ""
        if before == after:
            continue
        before_lines = before.splitlines(keepends=True)
        after_lines = after.splitlines(keepends=True)
        diff = "".join(difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile=f"live/{rel_path}",
            tofile=f"proposal/{rel_path}",
            lineterm="",
        ))
        files.append({
            "path": rel_path,
            "status": "added" if before_path is None else "deleted" if after_path is None else "modified",
            "diff": diff,
        })

    return {
        "proposal_id": proposal_id,
        "skill_name": skill_name,
        "source_dir": source_dir,
        "editable_skill_dir": editable_dir,
        "files": files,
    }


def _collect_diffable_files(root: str) -> Dict[str, str]:
    result = {}
    if not os.path.isdir(root):
        return result
    root = os.path.realpath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {"__pycache__", ".git", ".pytest_cache"}]
        for file_name in filenames:
            if file_name.endswith((".pyc", ".pyo")):
                continue
            ext = os.path.splitext(file_name)[1].lower()
            if ext not in _TEXT_DIFF_EXTENSIONS:
                continue
            path = os.path.realpath(os.path.join(dirpath, file_name))
            if not _is_relative_to(path, root):
                continue
            result[os.path.relpath(path, root).replace(os.sep, "/")] = path
    return result


def _read_diff_text(path: str, max_chars: int) -> str:
    try:
        text = _read_text(path)
    except Exception:
        return ""
    if len(text) > max_chars:
        return text[:max_chars] + "\n[diff truncated]\n"
    return text


def _find_proposal(proposal_id: str) -> str:
    proposal_id = _check_safe_name(proposal_id, "proposal id")
    matches = []
    proposals_root = get_proposals_root()
    if os.path.isdir(proposals_root):
        for skill_name in os.listdir(proposals_root):
            candidate = os.path.join(proposals_root, skill_name, proposal_id)
            if os.path.isdir(candidate):
                matches.append(candidate)
    if not matches:
        raise SkillEvolutionError(f"Proposal '{proposal_id}' was not found.")
    if len(matches) > 1:
        raise SkillEvolutionError(f"Proposal id '{proposal_id}' is ambiguous.")
    return _ensure_inside(matches[0], proposals_root, "proposal directory")


def _load_proposal_metadata(proposal_dir: str) -> Dict[str, str]:
    path = os.path.join(proposal_dir, "proposal.json")
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_proposal_metadata(proposal_dir: str, metadata: Dict[str, object]) -> None:
    _write_text(os.path.join(proposal_dir, "proposal.json"), json.dumps(metadata, indent=2))


def validate_skill_dir(skill_dir: str) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []

    if not os.path.isdir(skill_dir):
        return ValidationResult(False, [f"Skill directory not found: {skill_dir}"], warnings)

    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        errors.append("Missing SKILL.md")
    else:
        content = _read_text(skill_md)
        frontmatter = _parse_frontmatter(content)
        if not frontmatter.get("name"):
            errors.append("SKILL.md frontmatter is missing 'name'.")
        if not frontmatter.get("description"):
            warnings.append("SKILL.md frontmatter is missing 'description'.")

    for root, _, files in os.walk(skill_dir):
        if "__pycache__" in root.split(os.sep):
            continue
        for file_name in files:
            if not file_name.endswith(".py"):
                continue
            path = os.path.join(root, file_name)
            try:
                py_compile.compile(path, doraise=True)
            except py_compile.PyCompileError as e:
                errors.append(f"Python syntax error in {os.path.relpath(path, skill_dir)}: {e.msg}")

    return ValidationResult(not errors, errors, warnings)


def apply_proposal(proposal_id: str) -> ApplyResult:
    proposal_dir = _find_proposal(proposal_id)
    metadata = _load_proposal_metadata(proposal_dir)
    skill_name = _check_safe_name(metadata.get("skill_name", ""), "skill name")
    editable_skill_dir = os.path.join(proposal_dir, "skill")
    editable_skill_dir = _ensure_inside(editable_skill_dir, proposal_dir, "editable skill directory")

    validation = validate_skill_dir(editable_skill_dir)
    if not validation.ok:
        raise SkillEvolutionError("Proposal validation failed:\n- " + "\n- ".join(validation.errors))

    skills_dir = get_skills_dir()
    target_dir = os.path.join(skills_dir, skill_name)
    target_dir = _ensure_inside(target_dir, skills_dir, "target skill directory")
    if not os.path.isdir(target_dir):
        raise SkillEvolutionError(
            f"Live custom skill '{skill_name}' was not found at {target_dir}. "
            "Install or copy the skill into the custom skills directory before applying."
        )

    backup_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    backup_dir = os.path.join(get_versions_root(), skill_name, backup_id)
    backup_dir = _ensure_inside(backup_dir, get_versions_root(), "backup directory")
    os.makedirs(os.path.dirname(backup_dir), exist_ok=True)
    shutil.copytree(target_dir, backup_dir, ignore=_ignore_for_copy)

    shutil.rmtree(target_dir)
    shutil.copytree(editable_skill_dir, target_dir, ignore=_ignore_for_copy)

    metadata.update({
        "status": "applied",
        "applied_at": int(time.time()),
        "backup_id": backup_id,
        "backup_dir": backup_dir,
    })
    _save_proposal_metadata(proposal_dir, metadata)

    result = ApplyResult(
        skill_name=skill_name,
        proposal_id=proposal_id,
        backup_id=backup_id,
        backup_dir=backup_dir,
        target_dir=target_dir,
        warnings=validation.warnings,
    )
    record_event(
        "apply_completed",
        skill_name=skill_name,
        proposal_id=proposal_id,
        backup_id=backup_id,
        backup_dir=backup_dir,
        target_dir=target_dir,
        warnings=validation.warnings,
    )
    return result


def list_backups(name: str) -> List[Dict[str, str]]:
    name = _check_safe_name(name, "skill name")
    root = os.path.join(get_versions_root(), name)
    if not os.path.isdir(root):
        return []
    rows = []
    for backup_id in sorted(os.listdir(root), reverse=True):
        backup_dir = os.path.join(root, backup_id)
        if os.path.isdir(backup_dir):
            rows.append({"backup_id": backup_id, "path": backup_dir})
    return rows


def rollback_skill(name: str, backup_id: Optional[str] = None) -> RollbackResult:
    name = _check_safe_name(name, "skill name")
    backups = list_backups(name)
    if not backups:
        raise SkillEvolutionError(f"No backups found for skill '{name}'.")
    chosen = None
    if backup_id:
        backup_id = _check_safe_name(backup_id, "backup id")
        chosen = next((b for b in backups if b["backup_id"] == backup_id), None)
        if not chosen:
            raise SkillEvolutionError(f"Backup '{backup_id}' was not found for skill '{name}'.")
    else:
        chosen = backups[0]

    skills_dir = get_skills_dir()
    target_dir = _ensure_inside(os.path.join(skills_dir, name), skills_dir, "target skill directory")
    if not os.path.isdir(target_dir):
        raise SkillEvolutionError(f"Live skill '{name}' was not found at {target_dir}.")

    safety_backup_id = time.strftime("%Y%m%d-%H%M%S") + "-pre-rollback-" + uuid.uuid4().hex[:6]
    safety_backup_dir = _ensure_inside(
        os.path.join(get_versions_root(), name, safety_backup_id),
        get_versions_root(),
        "rollback safety backup directory",
    )
    os.makedirs(os.path.dirname(safety_backup_dir), exist_ok=True)
    shutil.copytree(target_dir, safety_backup_dir, ignore=_ignore_for_copy)

    shutil.rmtree(target_dir)
    shutil.copytree(chosen["path"], target_dir, ignore=_ignore_for_copy)

    result = RollbackResult(
        skill_name=name,
        backup_id=chosen["backup_id"],
        restored_from=chosen["path"],
        safety_backup_id=safety_backup_id,
        target_dir=target_dir,
    )
    record_event(
        "rollback_completed",
        skill_name=name,
        backup_id=chosen["backup_id"],
        restored_from=chosen["path"],
        safety_backup_id=safety_backup_id,
        target_dir=target_dir,
    )
    return result
