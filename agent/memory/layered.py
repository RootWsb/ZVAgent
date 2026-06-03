"""
Layered memory primitives.

This module adds structured mid-term episodic memory and profile memory without
changing the existing MEMORY.md flow. It is intentionally lightweight so future
extractor/scorer/consolidator training can build on stable JSON records.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from agent.memory.config import MemoryConfig, get_default_memory_config


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_filename() -> str:
    return datetime.now().strftime("%Y-%m-%d.jsonl")


def _estimate_tokens(text: str) -> int:
    """Small dependency-free token estimate for threshold decisions."""
    if not text:
        return 0
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    wordish = len(re.findall(r"[A-Za-z0-9_]+", text))
    other_chars = max(0, len(text) - cjk_chars)
    return cjk_chars + wordish + (other_chars // 4)


@dataclass
class EpisodicMemoryRecord:
    """Event-level mid-term memory record."""

    summary: str
    id: str = ""
    created_at: str = ""
    source: str = "chat"
    session_id: Optional[str] = None
    type: str = "event"
    entities: List[str] = field(default_factory=list)
    importance: float = 0.5
    stability: float = 0.5
    privacy: str = "normal"
    candidate_targets: List[str] = field(default_factory=list)
    raw_refs: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalized(self) -> "EpisodicMemoryRecord":
        if not self.id:
            self.id = f"evt_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:10]}"
        if not self.created_at:
            self.created_at = _utc_now_iso()
        self.summary = self.summary.strip()
        self.importance = max(0.0, min(1.0, float(self.importance)))
        self.stability = max(0.0, min(1.0, float(self.stability)))
        return self

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self.normalized())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EpisodicMemoryRecord":
        return cls(
            id=str(data.get("id") or ""),
            created_at=str(data.get("created_at") or ""),
            source=str(data.get("source") or "chat"),
            session_id=data.get("session_id"),
            type=str(data.get("type") or "event"),
            summary=str(data.get("summary") or ""),
            entities=list(data.get("entities") or []),
            importance=float(data.get("importance", 0.5)),
            stability=float(data.get("stability", 0.5)),
            privacy=str(data.get("privacy") or "normal"),
            candidate_targets=list(data.get("candidate_targets") or []),
            raw_refs=list(data.get("raw_refs") or []),
            metadata=dict(data.get("metadata") or {}),
        )


class EpisodicMemoryStore:
    """JSONL-backed mid-term memory store."""

    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or get_default_memory_config()
        self.root = self.config.get_episodic_dir()
        (self.root / "compacted").mkdir(parents=True, exist_ok=True)

    def append(
        self,
        summary: str,
        *,
        session_id: Optional[str] = None,
        source: str = "chat",
        memory_type: str = "event",
        entities: Optional[List[str]] = None,
        importance: float = 0.5,
        stability: float = 0.5,
        privacy: str = "normal",
        candidate_targets: Optional[List[str]] = None,
        raw_refs: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EpisodicMemoryRecord:
        record = EpisodicMemoryRecord(
            summary=summary,
            source=source,
            session_id=session_id,
            type=memory_type,
            entities=entities or [],
            importance=importance,
            stability=stability,
            privacy=privacy,
            candidate_targets=candidate_targets or [],
            raw_refs=raw_refs or [],
            metadata=metadata or {},
        ).normalized()
        if not record.summary:
            raise ValueError("summary is required")

        target = self.root / _today_filename()
        with target.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
        return record

    def iter_records(self, limit: Optional[int] = None) -> Iterable[EpisodicMemoryRecord]:
        count = 0
        files = sorted(self.root.glob("*.jsonl"), reverse=True)
        for file_path in files:
            for line in reversed(file_path.read_text(encoding="utf-8").splitlines()):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = EpisodicMemoryRecord.from_dict(json.loads(line))
                except Exception:
                    continue
                yield record
                count += 1
                if limit is not None and count >= limit:
                    return

    def list_recent(self, limit: int = 20) -> List[EpisodicMemoryRecord]:
        return list(self.iter_records(limit=max(0, limit)))

    def stats(self) -> Dict[str, Any]:
        records = list(self.iter_records())
        token_count = sum(_estimate_tokens(r.summary) for r in records)
        return {
            "items": len(records),
            "estimated_tokens": token_count,
            "root": str(self.root),
            "should_compact": self.should_compact(records=records, token_count=token_count),
        }

    def should_compact(
        self,
        *,
        records: Optional[List[EpisodicMemoryRecord]] = None,
        token_count: Optional[int] = None,
    ) -> bool:
        records = records if records is not None else list(self.iter_records())
        if token_count is None:
            token_count = sum(_estimate_tokens(r.summary) for r in records)
        return (
            len(records) > self.config.episodic_max_items
            or token_count > self.config.episodic_max_tokens
        )


def _empty_profile() -> Dict[str, Any]:
    return {
        "identity": {
            "name": None,
            "timezone": None,
            "language": None,
        },
        "preferences": [],
        "goals": [],
        "constraints": [],
        "relationships": [],
        "communication_style": {},
        "updated_at": None,
    }


class ProfileMemoryStore:
    """Structured JSON profile memory with a generated short summary."""

    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or get_default_memory_config()
        self.root = self.config.get_profile_dir()
        self.profile_path = self.root / "user_profile.json"
        self.summary_path = self.root / "profile_summary.md"
        self.history_path = self.root / "profile_history.jsonl"
        self._ensure_files()

    def _ensure_files(self):
        if not self.profile_path.exists():
            self.profile_path.write_text(
                json.dumps(_empty_profile(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        if not self.summary_path.exists():
            self.summary_path.write_text("", encoding="utf-8")
        if not self.history_path.exists():
            self.history_path.write_text("", encoding="utf-8")

    def load(self) -> Dict[str, Any]:
        try:
            return json.loads(self.profile_path.read_text(encoding="utf-8"))
        except Exception:
            return _empty_profile()

    def save(self, profile: Dict[str, Any], *, reason: str = "update") -> Dict[str, Any]:
        profile = dict(profile or {})
        profile.setdefault("identity", {})
        profile.setdefault("preferences", [])
        profile.setdefault("goals", [])
        profile.setdefault("constraints", [])
        profile.setdefault("relationships", [])
        profile.setdefault("communication_style", {})
        profile["updated_at"] = _utc_now_iso()

        self.profile_path.write_text(
            json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        self.history_path.open("a", encoding="utf-8").write(
            json.dumps(
                {"created_at": _utc_now_iso(), "reason": reason, "profile": profile},
                ensure_ascii=False,
            )
            + "\n"
        )
        self.write_summary(self.build_summary(profile))
        return profile

    def build_summary(self, profile: Optional[Dict[str, Any]] = None) -> str:
        profile = profile or self.load()
        lines = []

        identity = profile.get("identity") or {}
        language = identity.get("language")
        timezone = identity.get("timezone")
        if language or timezone:
            parts = []
            if language:
                parts.append(f"language={language}")
            if timezone:
                parts.append(f"timezone={timezone}")
            lines.append("- Identity: " + ", ".join(parts))

        for section, label in (
            ("preferences", "Preferences"),
            ("goals", "Goals"),
            ("constraints", "Constraints"),
        ):
            values = [
                str(item.get("value") or item.get("key") or "").strip()
                for item in profile.get(section, [])
                if isinstance(item, dict) and item.get("status", "active") == "active"
            ]
            values = [v for v in values if v]
            if values:
                lines.append(f"- {label}: " + "; ".join(values[:5]))

        style = profile.get("communication_style") or {}
        if style:
            style_parts = [f"{k}={v}" for k, v in style.items() if v]
            if style_parts:
                lines.append("- Communication: " + ", ".join(style_parts[:5]))

        return "\n".join(lines).strip()

    def write_summary(self, summary: str):
        self.summary_path.write_text(summary.strip() + ("\n" if summary.strip() else ""), encoding="utf-8")

    def read_summary(self) -> str:
        return self.summary_path.read_text(encoding="utf-8").strip()


class LayeredMemoryService:
    """Facade for the first layered-memory MVP."""

    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or get_default_memory_config()
        self.episodic = EpisodicMemoryStore(self.config)
        self.profile = ProfileMemoryStore(self.config)

    def get_status(self) -> Dict[str, Any]:
        return {
            "episodic": self.episodic.stats(),
            "profile": {
                "path": str(self.profile.profile_path),
                "summary_path": str(self.profile.summary_path),
                "summary_tokens": _estimate_tokens(self.profile.read_summary()),
            },
            "thresholds": {
                "episodic_max_items": self.config.episodic_max_items,
                "episodic_max_tokens": self.config.episodic_max_tokens,
                "episodic_keep_recent_items": self.config.episodic_keep_recent_items,
                "episodic_compact_target_tokens": self.config.episodic_compact_target_tokens,
                "profile_candidate_batch_size": self.config.profile_candidate_batch_size,
                "profile_min_confidence_to_write": self.config.profile_min_confidence_to_write,
                "long_term_max_items": self.config.long_term_max_items,
                "long_term_max_tokens": self.config.long_term_max_tokens,
            },
        }


__all__ = [
    "EpisodicMemoryRecord",
    "EpisodicMemoryStore",
    "ProfileMemoryStore",
    "LayeredMemoryService",
]
