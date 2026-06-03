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

    def list_all(self) -> List[EpisodicMemoryRecord]:
        """Return all active episodic records, newest first."""
        return list(self.iter_records())

    def list_recent(self, limit: int = 20) -> List[EpisodicMemoryRecord]:
        return list(self.iter_records(limit=max(0, limit)))

    def search(self, query: str, limit: int = 5) -> List[EpisodicMemoryRecord]:
        """Simple lexical search over recent episodic memories."""
        query = (query or "").strip().lower()
        if not query:
            return []

        tokens = set(re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z0-9_]+", query))
        results = []
        for record in self.iter_records():
            haystack = " ".join([
                record.summary,
                " ".join(record.entities),
                " ".join(record.candidate_targets),
                record.type,
            ]).lower()
            if any(token.lower() in haystack for token in tokens):
                results.append(record)
            if len(results) >= limit:
                break
        return results

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

    def compact(self, *, force: bool = False) -> Dict[str, Any]:
        """Compact older episodic records into markdown + raw JSONL snapshots.

        The newest ``episodic_keep_recent_items`` records remain active in JSONL.
        Older records are preserved under ``memory/episodic/compacted/`` and
        removed from active JSONL so search/statistics stay bounded.
        """
        records = self.list_all()
        token_count = sum(_estimate_tokens(r.summary) for r in records)
        if not records:
            return {"status": "skipped", "reason": "empty", "compacted": 0, "kept": 0}

        should_compact = self.should_compact(records=records, token_count=token_count)
        if not force and not should_compact:
            return {
                "status": "skipped",
                "reason": "below_threshold",
                "compacted": 0,
                "kept": len(records),
            }

        keep_count = max(0, self.config.episodic_keep_recent_items)
        kept = records[:keep_count]
        old = records[keep_count:]
        if not old:
            return {
                "status": "skipped",
                "reason": "nothing_old_enough",
                "compacted": 0,
                "kept": len(kept),
            }

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        compacted_dir = self.root / "compacted"
        compacted_dir.mkdir(parents=True, exist_ok=True)
        md_path = compacted_dir / f"{stamp}.md"
        raw_path = compacted_dir / f"{stamp}.jsonl"

        md_path.write_text(self._build_compacted_markdown(old, stamp), encoding="utf-8")
        with raw_path.open("w", encoding="utf-8") as f:
            for record in reversed(old):
                f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

        self._rewrite_active_records(kept)

        return {
            "status": "compacted",
            "compacted": len(old),
            "kept": len(kept),
            "markdown_path": str(md_path),
            "raw_path": str(raw_path),
            "estimated_tokens_before": token_count,
            "estimated_tokens_after": sum(_estimate_tokens(r.summary) for r in kept),
        }

    def _rewrite_active_records(self, records_newest_first: List[EpisodicMemoryRecord]):
        """Rewrite active root JSONL files with the provided records only."""
        for file_path in self.root.glob("*.jsonl"):
            file_path.unlink(missing_ok=True)

        by_day: Dict[str, List[EpisodicMemoryRecord]] = {}
        for record in reversed(records_newest_first):
            day = (record.created_at or _utc_now_iso())[:10]
            if not re.match(r"\d{4}-\d{2}-\d{2}", day):
                day = datetime.now().strftime("%Y-%m-%d")
            by_day.setdefault(day, []).append(record)

        for day, records in by_day.items():
            path = self.root / f"{day}.jsonl"
            with path.open("w", encoding="utf-8") as f:
                for record in records:
                    f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

    @staticmethod
    def _build_compacted_markdown(records_newest_first: List[EpisodicMemoryRecord], stamp: str) -> str:
        records = list(reversed(records_newest_first))
        lines = [
            f"# Episodic Memory Compaction: {stamp}",
            "",
            f"- Compacted records: {len(records)}",
            f"- Created at: {_utc_now_iso()}",
            "",
            "## Summary",
            "",
        ]

        for record in records:
            targets = ", ".join(record.candidate_targets) or "none"
            lines.append(
                f"- {record.summary} "
                f"(id={record.id}, importance={record.importance:.2f}, stability={record.stability:.2f}, targets={targets})"
            )

        profile_candidates = [r for r in records if "profile" in r.candidate_targets]
        long_term_candidates = [r for r in records if "long_term" in r.candidate_targets]

        if profile_candidates:
            lines.extend(["", "## Profile Candidates", ""])
            for record in profile_candidates:
                lines.append(f"- {record.summary} (evidence={record.id})")

        if long_term_candidates:
            lines.extend(["", "## Long-Term Candidates", ""])
            for record in long_term_candidates:
                lines.append(f"- {record.summary} (evidence={record.id})")

        lines.append("")
        return "\n".join(lines)


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

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search structured profile entries by simple lexical matching."""
        query = (query or "").strip().lower()
        if not query:
            return []

        tokens = set(re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z0-9_]+", query))
        profile = self.load()
        matches: List[Dict[str, Any]] = []
        for section in ("preferences", "goals", "constraints", "relationships"):
            for item in profile.get(section, []):
                if not isinstance(item, dict):
                    continue
                text = json.dumps(item, ensure_ascii=False).lower()
                if any(token.lower() in text for token in tokens):
                    result = dict(item)
                    result["_section"] = section
                    matches.append(result)
                if len(matches) >= limit:
                    return matches
        return matches


class LayeredMemoryService:
    """Facade for the first layered-memory MVP."""

    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or get_default_memory_config()
        self.episodic = EpisodicMemoryStore(self.config)
        self.profile = ProfileMemoryStore(self.config)
        self.jobs_dir = self.config.get_memory_jobs_dir()
        self.compaction_queue_path = self.jobs_dir / "compaction_queue.jsonl"

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

    def append_episodic_from_summary(
        self,
        summary: str,
        *,
        session_id: Optional[str] = None,
        source: str = "memory_flush",
        reason: str = "trim",
        importance: float = 0.6,
        stability: float = 0.5,
    ) -> List[EpisodicMemoryRecord]:
        """Append event-level memories from a flush summary.

        Each bullet line becomes one episodic record. This keeps L2 structured
        while preserving the existing daily Markdown memory behavior.
        """
        records = []
        for line in (summary or "").splitlines():
            text = line.strip()
            if not text:
                continue
            text = re.sub(r"^[-*]\s+", "", text).strip()
            if not text or text.startswith("#"):
                continue
            records.append(
                self.episodic.append(
                    text,
                    session_id=session_id,
                    source=source,
                    memory_type=reason,
                    importance=importance,
                    stability=stability,
                    candidate_targets=self._guess_candidate_targets(text),
                    metadata={"flush_reason": reason},
                )
            )
        if records and self.episodic.stats()["should_compact"]:
            self.enqueue_compaction_job(
                layer="episodic",
                reason="threshold",
                metadata={
                    "source": source,
                    "flush_reason": reason,
                    "new_records": len(records),
                },
            )
            self.process_compaction_queue()
        return records

    def search(self, query: str, layers: Optional[List[str]] = None, limit: int = 5) -> Dict[str, Any]:
        layers = layers or ["episodic", "profile"]
        result: Dict[str, Any] = {}
        if "episodic" in layers:
            result["episodic"] = self.episodic.search(query, limit=limit)
        if "profile" in layers:
            result["profile"] = self.profile.search(query, limit=limit)
        return result

    def enqueue_compaction_job(
        self,
        *,
        layer: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        job = {
            "id": f"compact_{layer}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
            "created_at": _utc_now_iso(),
            "layer": layer,
            "reason": reason,
            "status": "pending",
            "metadata": metadata or {},
        }
        with self.compaction_queue_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(job, ensure_ascii=False) + "\n")
        return job

    def process_compaction_queue(self, *, force: bool = False) -> Dict[str, Any]:
        """Process pending compaction jobs.

        First implementation supports episodic compaction. Unknown layers are
        marked failed so the queue never loops forever on an unsupported job.
        """
        jobs = self._load_compaction_jobs()
        if not jobs:
            return {"processed": 0, "compacted": 0, "jobs": []}

        processed = 0
        compacted = 0
        results = []
        for job in jobs:
            if job.get("status") != "pending":
                continue
            processed += 1
            try:
                if job.get("layer") == "episodic":
                    result = self.episodic.compact(force=force)
                else:
                    result = {
                        "status": "failed",
                        "reason": f"unsupported layer: {job.get('layer')}",
                    }
                job["status"] = "done" if result.get("status") in {"compacted", "skipped"} else "failed"
                job["processed_at"] = _utc_now_iso()
                job["result"] = result
                if result.get("status") == "compacted":
                    compacted += 1
                results.append({"job_id": job.get("id"), **result})
            except Exception as e:
                job["status"] = "failed"
                job["processed_at"] = _utc_now_iso()
                job["error"] = str(e)
                results.append({"job_id": job.get("id"), "status": "failed", "error": str(e)})

        self._write_compaction_jobs(jobs)
        return {"processed": processed, "compacted": compacted, "jobs": results}

    def _load_compaction_jobs(self) -> List[Dict[str, Any]]:
        if not self.compaction_queue_path.exists():
            return []
        jobs = []
        for line in self.compaction_queue_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                jobs.append(json.loads(line))
            except Exception:
                continue
        return jobs

    def _write_compaction_jobs(self, jobs: List[Dict[str, Any]]):
        with self.compaction_queue_path.open("w", encoding="utf-8") as f:
            for job in jobs:
                f.write(json.dumps(job, ensure_ascii=False) + "\n")

    @staticmethod
    def _guess_candidate_targets(text: str) -> List[str]:
        targets = []
        profile_markers = (
            "喜欢", "不喜欢", "偏好", "倾向", "希望", "目标", "计划",
            "以后", "用户认为", "用户希望", "用户计划",
        )
        long_term_markers = (
            "决定", "方案", "架构", "实现", "系统", "训练", "规则", "流程",
        )
        if any(marker in text for marker in profile_markers):
            targets.append("profile")
        if any(marker in text for marker in long_term_markers):
            targets.append("long_term")
        return targets


__all__ = [
    "EpisodicMemoryRecord",
    "EpisodicMemoryStore",
    "ProfileMemoryStore",
    "LayeredMemoryService",
]
