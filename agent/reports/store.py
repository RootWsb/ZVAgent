import json
import os
import secrets
import shutil
import threading
from datetime import datetime

from common.utils import expand_path
from config import conf


REPORTS_DIR_NAME = "reports"


def utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def reports_root() -> str:
    root = expand_path(conf().get("agent_workspace", "runtime/workspace"))
    path = os.path.join(root, REPORTS_DIR_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def safe_segment(value: str, fallback: str = "default") -> str:
    import re

    value = str(value or "").strip()
    if not value:
        return fallback
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value)
    return value[:120] or fallback


class ReportStore:
    _lock = threading.RLock()

    def __init__(self):
        self.root = reports_root()
        self.index_path = os.path.join(self.root, "jobs.json")

    def _load(self) -> dict:
        if not os.path.exists(self.index_path):
            return {"jobs": {}}
        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return {"jobs": {}}
            data.setdefault("jobs", {})
            return data
        except Exception:
            return {"jobs": {}}

    def _save(self, data: dict):
        tmp_path = self.index_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self.index_path)

    def create_job(self, user_id: str, channel_type: str, topic: str, display_name: str = "", options: dict = None) -> dict:
        now = datetime.now()
        job_id = "R" + now.strftime("%Y%m%d%H%M%S") + secrets.token_hex(3).upper()
        safe_user = safe_segment(user_id, "unknown_user")
        job_dir = os.path.join(self.root, safe_user, job_id)
        os.makedirs(job_dir, exist_ok=True)
        options = dict(options or {})
        job = {
            "job_id": job_id,
            "status": "queued",
            "topic": topic,
            "version": "V4",
            "options": options,
            "user_id": user_id,
            "display_name": display_name or user_id,
            "channel_type": channel_type,
            "token": secrets.token_urlsafe(24),
            "job_dir": job_dir,
            "md_path": os.path.join(job_dir, "report.md"),
            "html_path": os.path.join(job_dir, "report.html"),
            "pdf_path": os.path.join(job_dir, "report.pdf"),
            "sources_path": os.path.join(job_dir, "sources.json"),
            "plan_path": os.path.join(job_dir, "research_plan.json"),
            "error": "",
            "progress": "等待开始",
            "progress_percent": 0,
            "stage": "queued",
            "created_at": utc_now_iso(),
            "updated_at": utc_now_iso(),
            "finished_at": "",
        }
        with self._lock:
            data = self._load()
            data["jobs"][job_id] = job
            self._save(data)
        return job

    def find_recent_similar_job(
        self,
        user_id: str,
        topic: str,
        options: dict = None,
        within_seconds: int = 120,
    ) -> dict:
        """Find a recent same-user/same-topic job to make command retries idempotent."""
        options = dict(options or {})
        normalized_topic = " ".join(str(topic or "").split())
        now = datetime.utcnow()
        with self._lock:
            jobs = list(self._load().get("jobs", {}).values())

        candidates = []
        for job in jobs:
            if job.get("user_id") != user_id:
                continue
            if " ".join(str(job.get("topic", "")).split()) != normalized_topic:
                continue
            if dict(job.get("options") or {}) != options:
                continue
            if job.get("status") in ("done", "failed"):
                continue
            created_at = str(job.get("created_at", "")).replace("Z", "")
            try:
                created = datetime.fromisoformat(created_at)
            except Exception:
                continue
            age = (now - created).total_seconds()
            if 0 <= age <= within_seconds:
                candidates.append(job)

        candidates.sort(key=lambda item: item.get("created_at", ""), reverse=True)
        return dict(candidates[0]) if candidates else {}

    def update_job(self, job_id: str, **updates) -> dict:
        with self._lock:
            data = self._load()
            job = data.get("jobs", {}).get(job_id)
            if not job:
                raise KeyError(job_id)
            job.update(updates)
            job["updated_at"] = utc_now_iso()
            if updates.get("status") in ("done", "failed"):
                job["finished_at"] = utc_now_iso()
            data["jobs"][job_id] = job
            self._save(data)
            return dict(job)

    def get_job(self, job_id: str) -> dict:
        with self._lock:
            return dict(self._load().get("jobs", {}).get(job_id, {}))

    def find_user_job(self, user_id: str, job_id: str) -> dict:
        job = self.get_job(job_id)
        if job and job.get("user_id") == user_id:
            return job
        return {}

    def list_jobs(self, page: int = 1, page_size: int = 50, user_id: str = "") -> dict:
        page = max(1, int(page or 1))
        page_size = min(100, max(1, int(page_size or 50)))
        with self._lock:
            jobs = list(self._load().get("jobs", {}).values())
        if user_id:
            jobs = [job for job in jobs if job.get("user_id") == user_id]
        jobs.sort(key=lambda job: job.get("created_at", ""), reverse=True)
        total = len(jobs)
        start = (page - 1) * page_size
        items = [self._public_job(job) for job in jobs[start:start + page_size]]
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": start + page_size < total,
        }

    def delete_job(self, job_id: str) -> bool:
        with self._lock:
            data = self._load()
            job = data.get("jobs", {}).pop(job_id, None)
            if not job:
                return False
            self._save(data)

        job_dir = os.path.normpath(job.get("job_dir", ""))
        root = os.path.normpath(self.root)
        try:
            if job_dir and os.path.commonpath([os.path.abspath(root), os.path.abspath(job_dir)]) == os.path.abspath(root):
                shutil.rmtree(job_dir, ignore_errors=True)
        except Exception:
            pass
        return True

    @staticmethod
    def _public_job(job: dict) -> dict:
        safe = dict(job)
        safe.pop("token", None)
        return safe
