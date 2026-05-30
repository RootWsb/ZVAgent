"""
SessionService - Manages multi-session lifecycle for both web channel and cloud client.

Provides a unified interface for listing, deleting, renaming, clearing context,
and generating AI titles for conversation sessions. Backed by ConversationStore
(SQLite) and AgentBridge (in-memory agent instances).
"""

import re
from typing import Optional

from common.log import logger


_MOJIBAKE_RE = re.compile(r"[ÃÂâåæçèéäöüÅÆÇÈÉ]|[\u5fd9\u6c13\u732b\u8305\u9e93\u6402\u804a-\u807f]")


def _truncate_fallback_title(user_message: str, max_len: int = 30) -> str:
    """Pick the first non-empty line of the user message and truncate it."""
    if not user_message:
        return "New Chat"
    first_line = ""
    for line in user_message.splitlines():
        line = line.strip()
        if line:
            first_line = line
            break
    if not first_line:
        return "New Chat"
    if len(first_line) > max_len:
        first_line = first_line[:max_len].rstrip() + "..."
    return first_line


def _mojibake_score(text: str) -> int:
    """Heuristic score for titles that look like UTF-8 bytes decoded twice."""
    if not text:
        return 0
    score = len(_MOJIBAKE_RE.findall(text))
    score += text.count("\ufffd") * 2
    return score


def _looks_like_mojibake(text: str) -> bool:
    score = _mojibake_score(text)
    return score >= 2 and score / max(len(text), 1) >= 0.15


def _repair_mojibake(text: str) -> str:
    """
    Repair common Chinese mojibake produced by model/provider encoding bugs.

    Examples seen in the wild:
    - UTF-8 decoded as latin-1: "å å¯è´§å¸æ°é»"
    - UTF-8 decoded as GBK, then surfaced as latin-1-ish text.
    """
    title = text.strip()
    best = title
    best_score = _mojibake_score(title)

    candidates = [title]
    for enc in ("latin1", "gb18030", "cp1252"):
        try:
            decoded = title.encode(enc).decode("utf-8").strip()
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        if decoded and decoded not in candidates:
            candidates.append(decoded)
        # Some providers turn UTF-8 bytes into GBK text, and that result is
        # then displayed as latin-1-style mojibake by the UI.
        try:
            decoded_twice = decoded.encode("latin1").decode("utf-8").strip()
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        if decoded_twice and decoded_twice not in candidates:
            candidates.append(decoded_twice)

    for candidate in candidates:
        score = _mojibake_score(candidate)
        if score < best_score:
            best = candidate
            best_score = score

    return best


def generate_session_title(user_message: str, assistant_reply: str = "") -> str:
    """
    Generate a short session title by calling the current bot's reply_text.
    Falls back to the first line of the user message if the LLM call fails
    or returns an obvious error sentinel.
    """
    fallback = _truncate_fallback_title(user_message)
    try:
        from bridge.bridge import Bridge
        from models.session_manager import Session
        bot = Bridge().get_bot("chat")

        prompt_parts = [f"User: {user_message[:300]}"]
        if assistant_reply:
            prompt_parts.append(f"Assistant: {assistant_reply[:300]}")

        session = Session("__title_gen__", system_prompt="")
        session.messages = [
            {"role": "user", "content": (
                "Generate a very short title (max 15 characters for Chinese, max 6 words for English) "
                "summarizing this conversation. Return ONLY the title text, nothing else.\n\n"
                + "\n".join(prompt_parts)
            )}
        ]

        result = bot.reply_text(session) or {}
        # When bots fail (network error, auth error, rate limit, etc.) they
        # typically return completion_tokens=0 with a sentinel content like
        # "请再问我一次吧" / "我现在有点累了". Treat that as failure.
        completion_tokens = result.get("completion_tokens", 0) or 0
        raw = (result.get("content") or "").strip()
        if completion_tokens <= 0:
            logger.warning(
                f"[SessionService] Title generation got empty completion "
                f"(completion_tokens={completion_tokens}, content='{raw[:50]}'), "
                f"using fallback")
            return fallback

        title = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip().strip('"\'')
        title = _repair_mojibake(title)
        logger.info(f"[SessionService] Title generation result: '{title}' (len={len(title)})")
        if title and len(title) <= 50 and not _looks_like_mojibake(title):
            return title
        if title and _looks_like_mojibake(title):
            logger.warning(
                f"[SessionService] Title generation returned mojibake-like text "
                f"('{title[:50]}'), using fallback"
            )
    except Exception as e:
        logger.warning(f"[SessionService] Title generation failed: {e}")
    return fallback


class SessionService:
    """
    High-level service for session lifecycle management.

    Usage:
        svc = SessionService()
        result = svc.dispatch("list", {"channel_type": "web", "page": 1})
    """

    def _get_store(self):
        from agent.memory import get_conversation_store
        return get_conversation_store()

    def _remove_agent(self, session_id: str):
        """Remove the in-memory Agent instance for a session if it exists."""
        try:
            from bridge.bridge import Bridge
            ab = Bridge().get_agent_bridge()
            if session_id in ab.agents:
                del ab.agents[session_id]
                logger.info(f"[SessionService] Removed agent instance: {session_id}")
        except Exception:
            pass

    @staticmethod
    def _normalize_sid(session_id: str) -> str:
        if session_id and not session_id.startswith("session_"):
            return f"session_{session_id}"
        return session_id

    # ------------------------------------------------------------------
    # actions
    # ------------------------------------------------------------------
    def list_sessions(self, channel_type: Optional[str] = None,
                      page: int = 1, page_size: int = 50) -> dict:
        store = self._get_store()
        return store.list_sessions(
            channel_type=channel_type,
            page=page,
            page_size=page_size,
        )

    def delete_session(self, session_id: str) -> None:
        if not session_id:
            raise ValueError("session_id required")
        session_id = self._normalize_sid(session_id)

        store = self._get_store()
        store.clear_session(session_id)
        self._remove_agent(session_id)
        logger.info(f"[SessionService] Session deleted: {session_id}")

    def rename_session(self, session_id: str, title: str) -> None:
        if not session_id:
            raise ValueError("session_id required")
        if not title:
            raise ValueError("title required")
        session_id = self._normalize_sid(session_id)

        store = self._get_store()
        found = store.rename_session(session_id, title)
        if not found:
            raise ValueError("session not found")

    def clear_context(self, session_id: str) -> int:
        """
        Set context boundary. Returns the new context_start_seq value.
        """
        if not session_id:
            raise ValueError("session_id required")
        session_id = self._normalize_sid(session_id)

        store = self._get_store()
        new_seq = store.clear_context(session_id)
        self._remove_agent(session_id)
        return new_seq

    def gen_title(self, session_id: str, user_message: str,
                  assistant_reply: str = "") -> str:
        """
        Generate an AI title and persist it. Returns the generated title.
        """
        if not session_id:
            raise ValueError("session_id required")
        if not user_message:
            raise ValueError("user_message required")
        session_id = self._normalize_sid(session_id)

        title = generate_session_title(user_message, assistant_reply)

        store = self._get_store()
        updated = store.rename_session(session_id, title)
        logger.info(f"[SessionService] Title set: sid={session_id}, "
                     f"title='{title}', db_updated={updated}")
        return title

    # ------------------------------------------------------------------
    # dispatch — single entry point for protocol messages
    # ------------------------------------------------------------------
    def dispatch(self, action: str, payload: Optional[dict] = None) -> dict:
        """
        Dispatch a session management action and return a protocol-compatible
        response dict.

        Action names use a ``*_session`` / session-prefixed convention so they
        can coexist with history actions (e.g. ``query``) on the same HISTORY
        message channel without ambiguity.

        Supported actions:
          - list_sessions: list sessions with pagination
          - delete_session: delete a session
          - rename_session: rename a session title
          - clear_context: set context boundary
          - generate_title: AI-generate a session title

        :param action: one of the above action names
        :param payload: action-specific payload
        :return: dict with action, code, message, payload
        """
        payload = payload or {}
        try:
            if action == "list_sessions":
                result = self.list_sessions(
                    channel_type=payload.get("channel_type"),
                    page=int(payload.get("page", 1)),
                    page_size=int(payload.get("page_size", 50)),
                )
                return {"action": action, "code": 200, "message": "success", "payload": result}

            elif action == "delete_session":
                self.delete_session(payload.get("session_id", ""))
                return {"action": action, "code": 200, "message": "success", "payload": None}

            elif action == "rename_session":
                self.rename_session(
                    payload.get("session_id", ""),
                    payload.get("title", "").strip(),
                )
                return {"action": action, "code": 200, "message": "success", "payload": None}

            elif action == "clear_context":
                new_seq = self.clear_context(payload.get("session_id", ""))
                return {"action": action, "code": 200, "message": "success",
                        "payload": {"context_start_seq": new_seq}}

            elif action == "generate_title":
                title = self.gen_title(
                    payload.get("session_id", ""),
                    payload.get("user_message", ""),
                    payload.get("assistant_reply", ""),
                )
                return {"action": action, "code": 200, "message": "success",
                        "payload": {"title": title}}

            else:
                return {"action": action, "code": 400,
                        "message": f"unknown action: {action}", "payload": None}

        except ValueError as e:
            return {"action": action, "code": 400, "message": str(e), "payload": None}
        except Exception as e:
            logger.error(f"[SessionService] dispatch error: action={action}, error={e}")
            return {"action": action, "code": 500, "message": str(e), "payload": None}
