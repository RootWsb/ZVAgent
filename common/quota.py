# encoding:utf-8

import math
import os
import secrets
import hashlib
import sqlite3
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from common.log import logger
from common.user_identity import context_user_key
from common.utils import expand_path
from config import conf


ACTIVE = "active"
DISABLED = "disabled"


@dataclass
class QuotaCheck:
    allowed: bool
    user_id: str
    quota_tokens: int
    used_tokens: int
    remaining_tokens: int
    estimated_tokens: int
    message: str = ""


def estimate_text_tokens(text) -> int:
    """Small dependency-free token estimator for quota accounting.

    It intentionally overestimates a little for CJK text so quota checks are
    conservative even when the concrete model SDK does not expose usage.
    """
    if text is None:
        return 0
    text = str(text)
    if not text:
        return 0

    ascii_chars = 0
    cjk_chars = 0
    other_chars = 0
    for ch in text:
        code = ord(ch)
        if (
            0x4E00 <= code <= 0x9FFF
            or 0x3400 <= code <= 0x4DBF
            or 0x3040 <= code <= 0x30FF
            or 0xAC00 <= code <= 0xD7AF
        ):
            cjk_chars += 1
        elif code < 128:
            ascii_chars += 1
        else:
            other_chars += 1

    return max(1, math.ceil(ascii_chars / 4) + math.ceil(cjk_chars * 1.4) + math.ceil(other_chars / 2))


def estimate_context_tokens(context) -> int:
    base = estimate_text_tokens(getattr(context, "content", ""))
    attachments = context.get("attachments", []) if hasattr(context, "get") else []
    if isinstance(attachments, list):
        base += len(attachments) * int(conf().get("quota_attachment_tokens", 300))
    return base


def extract_reply_text(reply) -> str:
    if not reply:
        return ""
    if hasattr(reply, "agent_response") and reply.agent_response:
        return str(reply.agent_response)
    if hasattr(reply, "text_content") and reply.text_content:
        return str(reply.text_content)
    return str(getattr(reply, "content", "") or "")


def resolve_user_id(context) -> str:
    return context_user_key(context)


class QuotaManager:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or self._default_db_path()
        self._lock = threading.RLock()
        self._ensure_schema()

    @staticmethod
    def enabled() -> bool:
        return bool(conf().get("quota_enabled", False))

    @staticmethod
    def _default_db_path() -> str:
        root = expand_path(conf().get("agent_workspace", "runtime/workspace"))
        return os.path.join(root, "billing", "quota.db")

    def _connect(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        except PermissionError:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            fallback = os.path.join(project_root, "data", "billing", "quota.db")
            logger.warning(f"[quota] cannot write {self.db_path}, fallback to {fallback}")
            self.db_path = fallback
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self):
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        display_name TEXT DEFAULT '',
                        channel_type TEXT DEFAULT '',
                        quota_tokens INTEGER DEFAULT 0,
                        used_tokens INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'active',
                        created_at INTEGER NOT NULL,
                        updated_at INTEGER NOT NULL
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS usage_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        session_id TEXT DEFAULT '',
                        channel_type TEXT DEFAULT '',
                        model TEXT DEFAULT '',
                        input_tokens INTEGER DEFAULT 0,
                        output_tokens INTEGER DEFAULT 0,
                        total_tokens INTEGER DEFAULT 0,
                        reason TEXT DEFAULT 'chat',
                        created_at INTEGER NOT NULL
                    )
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_user_time ON usage_logs(user_id, created_at)")
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS redeem_codes (
                        code_hash TEXT PRIMARY KEY,
                        token_amount INTEGER NOT NULL,
                        status TEXT DEFAULT 'unused',
                        note TEXT DEFAULT '',
                        created_by TEXT DEFAULT '',
                        created_at INTEGER NOT NULL,
                        redeemed_by TEXT DEFAULT '',
                        redeemed_at INTEGER DEFAULT 0
                    )
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_redeem_status_time ON redeem_codes(status, created_at)")
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS skill_usage_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        session_id TEXT DEFAULT '',
                        channel_type TEXT DEFAULT '',
                        tool_name TEXT DEFAULT '',
                        status TEXT DEFAULT '',
                        arguments TEXT DEFAULT '',
                        result TEXT DEFAULT '',
                        execution_time REAL DEFAULT 0,
                        user_message TEXT DEFAULT '',
                        created_at INTEGER NOT NULL
                    )
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_skill_usage_user_time ON skill_usage_logs(user_id, created_at)")

    def ensure_user(self, user_id: str, channel_type: str = "", display_name: str = "") -> Dict:
        user_id = str(user_id or "anonymous")
        now = int(time.time())
        default_quota = int(conf().get("quota_default_tokens", 0) or 0)
        with self._lock:
            with self._connect() as conn:
                row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
                if not row:
                    conn.execute(
                        """
                        INSERT INTO users(user_id, display_name, channel_type, quota_tokens, used_tokens, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, 0, ?, ?, ?)
                        """,
                        (user_id, display_name, channel_type, default_quota, ACTIVE, now, now),
                    )
                elif channel_type or display_name:
                    conn.execute(
                        """
                        UPDATE users
                        SET display_name=COALESCE(NULLIF(?, ''), display_name),
                            channel_type=COALESCE(NULLIF(?, ''), channel_type),
                            updated_at=?
                        WHERE user_id=?
                        """,
                        (display_name, channel_type, now, user_id),
                    )
                row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
                return self._row_to_user(row)

    def get_user(self, user_id: str) -> Optional[Dict]:
        with self._lock:
            with self._connect() as conn:
                row = conn.execute("SELECT * FROM users WHERE user_id=?", (str(user_id),)).fetchone()
                return self._row_to_user(row) if row else None

    def list_users(self, limit: int = 200, offset: int = 0) -> List[Dict]:
        with self._lock:
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT * FROM users ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                    (int(limit), int(offset)),
                ).fetchall()
                return [self._row_to_user(row) for row in rows]

    def stats(self) -> Dict:
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    """
                    SELECT COUNT(*) AS total_users,
                           SUM(CASE WHEN status='active' THEN 1 ELSE 0 END) AS active_users,
                           COALESCE(SUM(quota_tokens), 0) AS total_quota,
                           COALESCE(SUM(used_tokens), 0) AS total_used
                    FROM users
                    """
                ).fetchone()
                return dict(row)

    def set_quota(self, user_id: str, quota_tokens: int, channel_type: str = "", display_name: str = "") -> Dict:
        self.ensure_user(user_id, channel_type=channel_type, display_name=display_name)
        now = int(time.time())
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    "UPDATE users SET quota_tokens=?, updated_at=? WHERE user_id=?",
                    (max(0, int(quota_tokens)), now, str(user_id)),
                )
        return self.get_user(user_id)

    def add_quota(self, user_id: str, delta_tokens: int, channel_type: str = "", display_name: str = "") -> Dict:
        self.ensure_user(user_id, channel_type=channel_type, display_name=display_name)
        now = int(time.time())
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    "UPDATE users SET quota_tokens=MAX(0, quota_tokens + ?), updated_at=? WHERE user_id=?",
                    (int(delta_tokens), now, str(user_id)),
                )
        return self.get_user(user_id)

    def set_status(self, user_id: str, status: str) -> Dict:
        status = status if status in (ACTIVE, DISABLED) else ACTIVE
        self.ensure_user(user_id)
        now = int(time.time())
        with self._lock:
            with self._connect() as conn:
                conn.execute("UPDATE users SET status=?, updated_at=? WHERE user_id=?", (status, now, str(user_id)))
        return self.get_user(user_id)

    def set_display_name(self, user_id: str, display_name: str) -> Dict:
        self.ensure_user(user_id)
        now = int(time.time())
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    "UPDATE users SET display_name=?, updated_at=? WHERE user_id=?",
                    (str(display_name or "").strip(), now, str(user_id)),
                )
        return self.get_user(user_id)

    def delete_user(self, user_id: str) -> bool:
        user_id = str(user_id or "")
        if not user_id:
            return False
        with self._lock:
            with self._connect() as conn:
                cur = conn.execute("DELETE FROM users WHERE user_id=?", (user_id,))
                conn.execute("DELETE FROM usage_logs WHERE user_id=?", (user_id,))
                return cur.rowcount > 0

    def consolidate_web_session_users(
        self,
        target_user_id: str = "web__user__console",
        display_name: str = "Web 控制台",
    ) -> Dict:
        """Merge legacy per-session web quota users into one stable console user.

        Older web requests used the chat session_id as the quota identity, which
        created one billing user per new web conversation. Keep the largest
        assigned quota to avoid inflating default quotas, but carry over all
        actual usage and logs.
        """
        target_user_id = str(target_user_id or "web__user__console")
        now = int(time.time())
        with self._lock:
            with self._connect() as conn:
                rows = conn.execute(
                    """
                    SELECT * FROM users
                    WHERE user_id LIKE 'web__user__session_%'
                       OR user_id LIKE 'web__user__Web_%'
                    """
                ).fetchall()
                if not rows:
                    conn.execute(
                        """
                        UPDATE redeem_codes
                        SET redeemed_by=?
                        WHERE redeemed_by LIKE 'web__user__session_%'
                           OR redeemed_by LIKE 'web__user__Web_%'
                        """,
                        (target_user_id,),
                    )
                    target = conn.execute("SELECT * FROM users WHERE user_id=?", (target_user_id,)).fetchone()
                    return {"merged": 0, "target": self._row_to_user(target) if target else None}

                target = conn.execute("SELECT * FROM users WHERE user_id=?", (target_user_id,)).fetchone()
                if not target:
                    default_quota = int(conf().get("quota_default_tokens", 0) or 0)
                    conn.execute(
                        """
                        INSERT INTO users(user_id, display_name, channel_type, quota_tokens, used_tokens, status, created_at, updated_at)
                        VALUES (?, ?, 'web', ?, 0, ?, ?, ?)
                        """,
                        (target_user_id, display_name, default_quota, ACTIVE, now, now),
                    )
                    target = conn.execute("SELECT * FROM users WHERE user_id=?", (target_user_id,)).fetchone()

                old_ids = [row["user_id"] for row in rows]
                quota_tokens = max([int(target["quota_tokens"] or 0)] + [int(row["quota_tokens"] or 0) for row in rows])
                used_tokens = int(target["used_tokens"] or 0) + sum(int(row["used_tokens"] or 0) for row in rows)
                status = ACTIVE if any(row["status"] == ACTIVE for row in rows) or target["status"] == ACTIVE else DISABLED

                conn.execute(
                    """
                    UPDATE users
                    SET display_name=?, channel_type='web', quota_tokens=?, used_tokens=?, status=?, updated_at=?
                    WHERE user_id=?
                    """,
                    (display_name, quota_tokens, used_tokens, status, now, target_user_id),
                )
                placeholders = ",".join("?" for _ in old_ids)
                conn.execute(
                    f"UPDATE usage_logs SET user_id=? WHERE user_id IN ({placeholders})",
                    [target_user_id] + old_ids,
                )
                conn.execute(
                    f"UPDATE skill_usage_logs SET user_id=? WHERE user_id IN ({placeholders})",
                    [target_user_id] + old_ids,
                )
                conn.execute(
                    f"UPDATE redeem_codes SET redeemed_by=? WHERE redeemed_by IN ({placeholders})",
                    [target_user_id] + old_ids,
                )
                conn.execute(
                    """
                    UPDATE redeem_codes
                    SET redeemed_by=?
                    WHERE redeemed_by LIKE 'web__user__session_%'
                       OR redeemed_by LIKE 'web__user__Web_%'
                    """,
                    (target_user_id,),
                )
                conn.execute(f"DELETE FROM users WHERE user_id IN ({placeholders})", old_ids)
                user = conn.execute("SELECT * FROM users WHERE user_id=?", (target_user_id,)).fetchone()
                return {"merged": len(old_ids), "target": self._row_to_user(user)}

    def check(self, user_id: str, estimated_tokens: int, channel_type: str = "", display_name: str = "") -> QuotaCheck:
        user = self.ensure_user(user_id, channel_type=channel_type, display_name=display_name)
        remaining = int(user["remaining_tokens"])
        estimated_tokens = max(1, int(estimated_tokens))
        if user["status"] != ACTIVE:
            return QuotaCheck(False, user["user_id"], user["quota_tokens"], user["used_tokens"], remaining, estimated_tokens, "账号已停用，请联系管理员。")
        if remaining < estimated_tokens:
            return QuotaCheck(
                False,
                user["user_id"],
                user["quota_tokens"],
                user["used_tokens"],
                remaining,
                estimated_tokens,
                f"Token 额度不足：剩余 {remaining}，本次预计需要 {estimated_tokens}。请联系管理员充值或提升额度。",
            )
        return QuotaCheck(True, user["user_id"], user["quota_tokens"], user["used_tokens"], remaining, estimated_tokens)

    def record_usage(
        self,
        user_id: str,
        session_id: str = "",
        channel_type: str = "",
        model: str = "",
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_tokens: int = 0,
        reason: str = "chat",
    ) -> Dict:
        user_id = str(user_id or "anonymous")
        self.ensure_user(user_id, channel_type=channel_type)
        total_tokens = max(0, int(total_tokens or (int(input_tokens) + int(output_tokens))))
        now = int(time.time())
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO usage_logs(user_id, session_id, channel_type, model, input_tokens, output_tokens, total_tokens, reason, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        str(session_id or ""),
                        str(channel_type or ""),
                        str(model or ""),
                        int(input_tokens),
                        int(output_tokens),
                        total_tokens,
                        str(reason or "chat"),
                        now,
                    ),
                )
                conn.execute(
                    "UPDATE users SET used_tokens=used_tokens + ?, updated_at=? WHERE user_id=?",
                    (total_tokens, now, user_id),
                )
        return self.get_user(user_id)

    def usage_logs(self, user_id: str = "", limit: int = 100) -> List[Dict]:
        with self._lock:
            with self._connect() as conn:
                if user_id:
                    rows = conn.execute(
                        "SELECT * FROM usage_logs WHERE user_id=? ORDER BY id DESC LIMIT ?",
                        (str(user_id), int(limit)),
                    ).fetchall()
                else:
                    rows = conn.execute("SELECT * FROM usage_logs ORDER BY id DESC LIMIT ?", (int(limit),)).fetchall()
                return [dict(row) for row in rows]

    @staticmethod
    def _normalize_redeem_code(code: str) -> str:
        return str(code or "").strip().upper().replace(" ", "").replace("-", "")

    @classmethod
    def _hash_redeem_code(cls, code: str) -> str:
        normalized = cls._normalize_redeem_code(code)
        pepper = str(conf().get("quota_redeem_secret", "") or "")
        return hashlib.sha256((pepper + ":" + normalized).encode("utf-8")).hexdigest()

    @staticmethod
    def _format_redeem_code(raw: str) -> str:
        chunks = [raw[i:i + 4] for i in range(0, len(raw), 4)]
        return "ZV-" + "-".join(chunks)

    def generate_redeem_codes(
        self,
        token_amount: int,
        count: int = 1,
        created_by: str = "admin",
        note: str = "",
    ) -> List[Dict]:
        token_amount = max(1, int(token_amount))
        count = max(1, min(int(count or 1), int(conf().get("quota_redeem_max_batch", 100) or 100)))
        now = int(time.time())
        generated = []
        with self._lock:
            with self._connect() as conn:
                while len(generated) < count:
                    code = self._format_redeem_code(secrets.token_hex(8).upper())
                    code_hash = self._hash_redeem_code(code)
                    try:
                        conn.execute(
                            """
                            INSERT INTO redeem_codes(code_hash, token_amount, status, note, created_by, created_at)
                            VALUES (?, ?, 'unused', ?, ?, ?)
                            """,
                            (code_hash, token_amount, str(note or ""), str(created_by or "admin"), now),
                        )
                    except sqlite3.IntegrityError:
                        continue
                    generated.append({
                        "code": code,
                        "token_amount": token_amount,
                        "status": "unused",
                        "note": note or "",
                        "created_by": created_by or "admin",
                        "created_at": now,
                    })
        return generated

    def redeem_code(self, code: str, user_id: str, channel_type: str = "", display_name: str = "") -> Dict:
        normalized = self._normalize_redeem_code(code)
        if not normalized:
            return {"status": "error", "message": "兑换码不能为空"}
        user_id = str(user_id or "anonymous")
        self.ensure_user(user_id, channel_type=channel_type, display_name=display_name)
        code_hash = self._hash_redeem_code(normalized)
        now = int(time.time())
        with self._lock:
            with self._connect() as conn:
                row = conn.execute("SELECT * FROM redeem_codes WHERE code_hash=?", (code_hash,)).fetchone()
                if not row:
                    return {"status": "error", "message": "兑换码无效"}
                data = dict(row)
                if data.get("status") != "unused":
                    return {"status": "error", "message": "兑换码已被使用或已失效"}
                cur = conn.execute(
                    """
                    UPDATE redeem_codes
                    SET status='redeemed', redeemed_by=?, redeemed_at=?
                    WHERE code_hash=? AND status='unused'
                    """,
                    (user_id, now, code_hash),
                )
                if cur.rowcount <= 0:
                    return {"status": "error", "message": "兑换码已被使用或已失效"}
                conn.execute(
                    "UPDATE users SET quota_tokens=quota_tokens + ?, updated_at=? WHERE user_id=?",
                    (int(data["token_amount"]), now, user_id),
                )
        return {
            "status": "success",
            "token_amount": int(data["token_amount"]),
            "user": self.get_user(user_id),
        }

    def list_redeem_codes(self, limit: int = 100, include_redeemed: bool = True) -> List[Dict]:
        limit = max(1, min(int(limit or 100), 500))
        with self._lock:
            with self._connect() as conn:
                if include_redeemed:
                    rows = conn.execute(
                        "SELECT token_amount, status, note, created_by, created_at, redeemed_by, redeemed_at FROM redeem_codes ORDER BY created_at DESC LIMIT ?",
                        (limit,),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT token_amount, status, note, created_by, created_at, redeemed_by, redeemed_at FROM redeem_codes WHERE status='unused' ORDER BY created_at DESC LIMIT ?",
                        (limit,),
                    ).fetchall()
                return [dict(row) for row in rows]

    def record_skill_usage(
        self,
        user_id: str,
        session_id: str = "",
        channel_type: str = "",
        tool_name: str = "",
        status: str = "",
        arguments="",
        result="",
        execution_time: float = 0,
        user_message: str = "",
    ):
        if not conf().get("training_data_enabled", True):
            return
        user_id = str(user_id or "anonymous")
        now = int(time.time())
        def encode(value, max_chars=4000):
            try:
                import json
                text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
            except Exception:
                text = str(value)
            return text[:max_chars]
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO skill_usage_logs(user_id, session_id, channel_type, tool_name, status, arguments, result, execution_time, user_message, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        str(session_id or ""),
                        str(channel_type or ""),
                        str(tool_name or ""),
                        str(status or ""),
                        encode(arguments),
                        encode(result),
                        float(execution_time or 0),
                        encode(user_message, max_chars=2000),
                        now,
                    ),
                )

    def skill_usage_logs(self, user_id: str = "", limit: int = 100) -> List[Dict]:
        limit = max(1, min(int(limit or 100), 500))
        with self._lock:
            with self._connect() as conn:
                if user_id:
                    rows = conn.execute(
                        "SELECT * FROM skill_usage_logs WHERE user_id=? ORDER BY id DESC LIMIT ?",
                        (str(user_id), limit),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT * FROM skill_usage_logs ORDER BY id DESC LIMIT ?",
                        (limit,),
                    ).fetchall()
                return [dict(row) for row in rows]

    @staticmethod
    def _row_to_user(row) -> Dict:
        data = dict(row)
        data["quota_tokens"] = int(data.get("quota_tokens") or 0)
        data["used_tokens"] = int(data.get("used_tokens") or 0)
        data["remaining_tokens"] = max(0, data["quota_tokens"] - data["used_tokens"])
        return data


_manager = None
_manager_requested_path = None


def get_quota_manager() -> QuotaManager:
    global _manager, _manager_requested_path
    db_path = QuotaManager._default_db_path()
    if _manager is None or _manager_requested_path != db_path:
        try:
            _manager = QuotaManager(db_path)
            _manager_requested_path = db_path
        except Exception as e:
            logger.error(f"[quota] failed to initialize quota manager: {e}", exc_info=True)
            raise
    return _manager
