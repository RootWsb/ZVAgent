"""
Structured Level 1 / Level 2 summary support for skills.

This module defines a grounded summary artifact that can be generated
offline from SKILL.md and safely consumed at runtime for progressive
skill loading.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


SUMMARY_SCHEMA_VERSION = "1.0"

EVIDENCE_FIELDS = (
    "use_when",
    "avoid_when",
    "prerequisites",
    "key_inputs",
    "workflow_outline",
    "tool_dependencies",
    "risk_flags",
)


@dataclass
class SkillSummaryGenerator:
    """Metadata about the model or pipeline that generated the summary."""

    provider: str
    model: str
    prompt_version: str


@dataclass
class SkillLevel1Card:
    """Minimal prompt-safe routing card."""

    name: str
    description: str
    tags: List[str] = field(default_factory=list)


@dataclass
class SkillLevel2Card:
    """Structured pre-read summary used before opening full SKILL.md."""

    one_line: str
    use_when: List[str] = field(default_factory=list)
    avoid_when: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    key_inputs: List[str] = field(default_factory=list)
    workflow_outline: List[str] = field(default_factory=list)
    tool_dependencies: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)


@dataclass
class SkillSummaryArtifact:
    """Persisted summary sidecar for one skill."""

    schema_version: str
    skill_name: str
    source_path: str
    source_hash: str
    generated_at: str
    generator: SkillSummaryGenerator
    level_1: SkillLevel1Card
    level_2: SkillLevel2Card
    evidence: Dict[str, List[str]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SkillSummaryArtifact":
        generator = SkillSummaryGenerator(**data["generator"])
        level_1 = SkillLevel1Card(**data["level_1"])
        level_2 = SkillLevel2Card(**data["level_2"])
        evidence = {
            str(key): [str(item) for item in (value or [])]
            for key, value in dict(data.get("evidence", {})).items()
        }
        return cls(
            schema_version=str(data["schema_version"]),
            skill_name=str(data["skill_name"]),
            source_path=str(data["source_path"]),
            source_hash=str(data["source_hash"]),
            generated_at=str(data["generated_at"]),
            generator=generator,
            level_1=level_1,
            level_2=level_2,
            evidence=evidence,
        )


@dataclass
class SkillSummaryValidationResult:
    """Validation result for a summary artifact."""

    ok: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def compute_skill_source_hash(content: str) -> str:
    """Hash raw SKILL.md content for cache invalidation."""

    return hashlib.sha256((content or "").encode("utf-8")).hexdigest()


def read_skill_summary(path: str) -> SkillSummaryArtifact:
    """Load a summary artifact from disk."""

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return SkillSummaryArtifact.from_dict(data)


def write_skill_summary(path: str, artifact: SkillSummaryArtifact):
    """Write a summary artifact to disk."""

    summary_path = Path(path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(artifact.to_dict(), f, indent=2, ensure_ascii=False)


def validate_skill_summary(
    artifact: SkillSummaryArtifact,
    *,
    skill_content: Optional[str] = None,
    skill_name: Optional[str] = None,
    source_hash: Optional[str] = None,
    require_grounding: bool = True,
) -> SkillSummaryValidationResult:
    """
    Validate a summary artifact.

    The validator is intentionally conservative. Level 2 summaries are only
    meant to route and triage skills, not replace the full SKILL.md.
    """

    errors: List[str] = []
    warnings: List[str] = []

    if artifact.schema_version != SUMMARY_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {SUMMARY_SCHEMA_VERSION}, got {artifact.schema_version}"
        )

    expected_skill_name = (skill_name or artifact.level_1.name or "").strip()
    if not artifact.skill_name.strip():
        errors.append("skill_name is required")
    elif expected_skill_name and artifact.skill_name != expected_skill_name:
        errors.append(
            f"skill_name mismatch: expected '{expected_skill_name}', got '{artifact.skill_name}'"
        )

    if not artifact.source_path.strip():
        errors.append("source_path is required")
    if not artifact.source_hash.strip():
        errors.append("source_hash is required")
    if source_hash and artifact.source_hash != source_hash:
        errors.append("source_hash does not match the current SKILL.md content")
    if not artifact.generated_at.strip():
        errors.append("generated_at is required")

    if not artifact.generator.provider.strip():
        errors.append("generator.provider is required")
    if not artifact.generator.model.strip():
        errors.append("generator.model is required")
    if not artifact.generator.prompt_version.strip():
        errors.append("generator.prompt_version is required")

    _validate_level_1(artifact.level_1, errors, warnings)
    _validate_level_2(artifact.level_2, errors, warnings)
    _validate_evidence_shape(artifact.evidence, errors, warnings)

    if require_grounding:
        normalized_content = _normalize_text(skill_content or "")
        if not normalized_content:
            warnings.append("grounding was requested but skill_content is empty")
        else:
            _validate_evidence_grounding(artifact, normalized_content, errors, warnings)

    return SkillSummaryValidationResult(ok=not errors, errors=errors, warnings=warnings)


def _validate_level_1(level_1: SkillLevel1Card, errors: List[str], warnings: List[str]):
    if not level_1.name.strip():
        errors.append("level_1.name is required")
    if not level_1.description.strip():
        errors.append("level_1.description is required")
    elif len(level_1.description.strip()) > 240:
        warnings.append("level_1.description is longer than 240 chars")
    if len(level_1.tags) > 12:
        warnings.append("level_1.tags should stay compact (<= 12)")


def _validate_level_2(level_2: SkillLevel2Card, errors: List[str], warnings: List[str]):
    if not level_2.one_line.strip():
        errors.append("level_2.one_line is required")
    elif len(level_2.one_line.strip()) > 220:
        warnings.append("level_2.one_line is longer than 220 chars")

    limits = {
        "use_when": 8,
        "avoid_when": 6,
        "prerequisites": 8,
        "key_inputs": 8,
        "workflow_outline": 10,
        "tool_dependencies": 8,
        "risk_flags": 8,
    }
    for field_name, max_items in limits.items():
        values = getattr(level_2, field_name)
        if len(values) > max_items:
            warnings.append(f"level_2.{field_name} has {len(values)} items; keep <= {max_items}")
        for index, value in enumerate(values):
            if not str(value).strip():
                errors.append(f"level_2.{field_name}[{index}] is empty")


def _validate_evidence_shape(
    evidence: Dict[str, List[str]],
    errors: List[str],
    warnings: List[str],
):
    for field_name in evidence.keys():
        if field_name not in EVIDENCE_FIELDS:
            warnings.append(f"evidence contains unknown field '{field_name}'")
    for field_name in EVIDENCE_FIELDS:
        snippets = evidence.get(field_name, [])
        if not isinstance(snippets, list):
            errors.append(f"evidence.{field_name} must be a list")
            continue
        if len(snippets) > 8:
            warnings.append(f"evidence.{field_name} should stay compact (<= 8)")
        for index, snippet in enumerate(snippets):
            if not str(snippet).strip():
                errors.append(f"evidence.{field_name}[{index}] is empty")


def _validate_evidence_grounding(
    artifact: SkillSummaryArtifact,
    normalized_content: str,
    errors: List[str],
    warnings: List[str],
):
    level_2 = artifact.level_2
    for field_name in EVIDENCE_FIELDS:
        values = getattr(level_2, field_name)
        if not values:
            continue
        snippets = artifact.evidence.get(field_name, [])
        if not snippets:
            warnings.append(f"level_2.{field_name} has content but no evidence snippets")
            continue
        grounded = False
        for snippet in snippets:
            normalized_snippet = _normalize_text(snippet)
            if normalized_snippet and normalized_snippet in normalized_content:
                grounded = True
                break
        if not grounded:
            errors.append(
                f"evidence.{field_name} does not match any normalized snippet in SKILL.md"
            )


def _normalize_text(text: str) -> str:
    return " ".join(str(text or "").split()).strip().lower()
