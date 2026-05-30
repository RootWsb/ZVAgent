"""
Offline Level 2 summary generation for skills.

This module turns a SKILL.md file into a validated SKILL.summary.json
artifact. Generation is intentionally offline-only and must never be used
as the final execution authority for a skill.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.protocol.models import LLMRequest
from agent.skills.summary import (
    EVIDENCE_FIELDS,
    SUMMARY_SCHEMA_VERSION,
    SkillLevel1Card,
    SkillLevel2Card,
    SkillSummaryArtifact,
    SkillSummaryGenerator,
    SkillSummaryValidationResult,
    compute_skill_source_hash,
    read_skill_summary,
    validate_skill_summary,
)


SUMMARY_GENERATOR_PROMPT_VERSION = "skill-summary-v1"

SUMMARY_SYSTEM_PROMPT = """You generate conservative JSON summaries for agent skills.

Rules:
- Output valid JSON only. No markdown, no prose before or after the JSON.
- Only use facts explicitly grounded in the provided SKILL.md content.
- If a field is not clearly supported by the SKILL.md, leave it empty.
- Level 2 summaries are only for routing and triage, never execution authority.
- Keep descriptions compact and literal.
- Evidence snippets must be exact substrings copied from SKILL.md.
"""

SUMMARY_USER_PROMPT = """Summarize this skill into the exact JSON shape below.

Return JSON with these top-level keys only:
{{
  "level_1": {{
    "name": "...",
    "description": "...",
    "tags": ["..."]
  }},
  "level_2": {{
    "one_line": "...",
    "use_when": ["..."],
    "avoid_when": ["..."],
    "prerequisites": ["..."],
    "key_inputs": ["..."],
    "workflow_outline": ["..."],
    "tool_dependencies": ["..."],
    "risk_flags": ["..."]
  }},
  "evidence": {{
    "use_when": ["exact quote from source"],
    "avoid_when": ["exact quote from source"],
    "prerequisites": ["exact quote from source"],
    "key_inputs": ["exact quote from source"],
    "workflow_outline": ["exact quote from source"],
    "tool_dependencies": ["exact quote from source"],
    "risk_flags": ["exact quote from source"]
  }}
}}

Constraints:
- level_1.description should be a short one-line routing description.
- level_2.one_line should be one sentence.
- Prefer omission over inference.
- Evidence must be copied verbatim from the source.

Skill path: {skill_path}
Skill name: {skill_name}

SKILL.md:
```md
{skill_content}
```
"""


class SkillSummaryGenerationError(Exception):
    """Raised when summary generation or validation fails."""


@dataclass
class SkillSummaryGenerationResult:
    """Result of one summary generation attempt."""

    artifact: Optional[SkillSummaryArtifact]
    validation: Optional[SkillSummaryValidationResult]
    raw_response: str
    skipped: bool = False
    skip_reason: str = ""


def get_skill_summary_path(skill_dir: str) -> str:
    """Return the sidecar summary path for one skill directory."""

    return os.path.join(skill_dir, "SKILL.summary.json")


def generate_skill_summary(
    skill_dir: str,
    *,
    llm_model: Any,
    provider: str,
    model_name: str,
    force: bool = False,
    generated_at: Optional[str] = None,
    prompt_version: str = SUMMARY_GENERATOR_PROMPT_VERSION,
) -> SkillSummaryGenerationResult:
    """
    Generate a grounded summary artifact for one skill directory.

    The caller is responsible for persisting the artifact after this function
    returns successfully.
    """

    skill_path = Path(skill_dir) / "SKILL.md"
    if not skill_path.is_file():
        raise SkillSummaryGenerationError(f"SKILL.md not found: {skill_path}")

    skill_content = skill_path.read_text(encoding="utf-8")
    skill_name = _extract_skill_name(skill_content, fallback=Path(skill_dir).name)
    source_hash = compute_skill_source_hash(skill_content)
    summary_path = Path(get_skill_summary_path(skill_dir))

    if not force and summary_path.is_file():
        existing = _read_existing_summary_if_valid(
            summary_path,
            skill_content=skill_content,
            skill_name=skill_name,
            source_hash=source_hash,
        )
        if existing is not None:
            return SkillSummaryGenerationResult(
                artifact=existing,
                validation=None,
                raw_response="",
                skipped=True,
                skip_reason="up-to-date",
            )

    request = LLMRequest(
        messages=[
            {
                "role": "user",
                "content": SUMMARY_USER_PROMPT.format(
                    skill_path=str(skill_path.resolve()),
                    skill_name=skill_name,
                    skill_content=skill_content,
                ),
            }
        ],
        temperature=0,
        max_tokens=1600,
        stream=False,
        system=SUMMARY_SYSTEM_PROMPT,
    )
    response = llm_model.call(request)
    raw_response = _extract_response_text(response)
    if not raw_response.strip():
        raise SkillSummaryGenerationError("model returned an empty summary response")

    payload = _parse_summary_payload(raw_response)
    artifact = _build_artifact(
        payload,
        skill_name=skill_name,
        source_path=str(skill_path.resolve()),
        source_hash=source_hash,
        provider=provider,
        model_name=model_name,
        generated_at=generated_at or _utc_now_iso(),
        prompt_version=prompt_version,
    )

    validation = validate_skill_summary(
        artifact,
        skill_content=skill_content,
        skill_name=skill_name,
        source_hash=source_hash,
        require_grounding=True,
    )
    if not validation.ok:
        details = "; ".join(validation.errors)
        raise SkillSummaryGenerationError(f"summary validation failed: {details}")

    return SkillSummaryGenerationResult(
        artifact=artifact,
        validation=validation,
        raw_response=raw_response,
    )


def _read_existing_summary_if_valid(
    summary_path: Path,
    *,
    skill_content: str,
    skill_name: str,
    source_hash: str,
) -> Optional[SkillSummaryArtifact]:
    try:
        artifact = read_skill_summary(str(summary_path))
    except Exception:
        return None

    validation = validate_skill_summary(
        artifact,
        skill_content=skill_content,
        skill_name=skill_name,
        source_hash=source_hash,
        require_grounding=True,
    )
    if validation.ok:
        return artifact
    return None


def _extract_skill_name(skill_content: str, *, fallback: str) -> str:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", skill_content, re.DOTALL)
    if match:
        for line in match.group(1).splitlines():
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            if key.strip() == "name":
                name = value.strip().strip('"').strip("'")
                if name:
                    return name
    return fallback


def _extract_response_text(response: Any) -> str:
    if isinstance(response, dict):
        if response.get("error"):
            raise SkillSummaryGenerationError(str(response.get("message") or "model call failed"))

        content = response.get("content")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    return str(block.get("text", ""))

        choices = response.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content", "")
            if isinstance(content, list):
                parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        parts.append(str(block.get("text", "")))
                return "\n".join(parts)
            return str(content or "")

    if hasattr(response, "choices") and getattr(response, "choices", None):
        choice = response.choices[0]
        if hasattr(choice, "message") and getattr(choice.message, "content", None):
            return str(choice.message.content)

    return ""


def _parse_summary_payload(text: str) -> Dict[str, Any]:
    raw = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.DOTALL)
    if fenced:
        raw = fenced.group(1).strip()
    elif raw and raw[0] != "{":
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            raw = raw[start:end + 1]

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SkillSummaryGenerationError(f"summary response is not valid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise SkillSummaryGenerationError("summary response must be a JSON object")
    return payload


def _build_artifact(
    payload: Dict[str, Any],
    *,
    skill_name: str,
    source_path: str,
    source_hash: str,
    provider: str,
    model_name: str,
    generated_at: str,
    prompt_version: str,
) -> SkillSummaryArtifact:
    level_1_payload = dict(payload.get("level_1") or {})
    level_2_payload = dict(payload.get("level_2") or {})
    evidence_payload = dict(payload.get("evidence") or {})

    level_2 = SkillLevel2Card(
        one_line=_coerce_text(level_2_payload.get("one_line")),
        use_when=_coerce_list(level_2_payload.get("use_when")),
        avoid_when=_coerce_list(level_2_payload.get("avoid_when")),
        prerequisites=_coerce_list(level_2_payload.get("prerequisites")),
        key_inputs=_coerce_list(level_2_payload.get("key_inputs")),
        workflow_outline=_coerce_list(level_2_payload.get("workflow_outline")),
        tool_dependencies=_coerce_list(level_2_payload.get("tool_dependencies")),
        risk_flags=_coerce_list(level_2_payload.get("risk_flags")),
    )
    level_1 = SkillLevel1Card(
        name=_coerce_text(level_1_payload.get("name")) or skill_name,
        description=(
            _coerce_text(level_1_payload.get("description"))
            or level_2.one_line
        ),
        tags=_coerce_list(level_1_payload.get("tags")),
    )
    evidence = {
        field_name: _coerce_list(evidence_payload.get(field_name))
        for field_name in EVIDENCE_FIELDS
    }

    return SkillSummaryArtifact(
        schema_version=SUMMARY_SCHEMA_VERSION,
        skill_name=skill_name,
        source_path=source_path,
        source_hash=source_hash,
        generated_at=generated_at,
        generator=SkillSummaryGenerator(
            provider=provider,
            model=model_name,
            prompt_version=prompt_version,
        ),
        level_1=level_1,
        level_2=level_2,
        evidence=evidence,
    )


def _coerce_text(value: Any) -> str:
    return str(value or "").strip()


def _coerce_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
