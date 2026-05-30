"""
Turn Event Reporter - POSTs turn events to a local bypass endpoint.

Each time the agent finishes a reply, a ``company_agent_turn`` event is
sent to the configured URL (default ``http://127.0.0.1:9119/api/sidecar/events``).

The POST is fire-and-forget: failures are logged but never block the
reply pipeline.
"""

import json
import threading
import uuid
from datetime import datetime, timezone

import requests

from common.log import logger


_DEFAULT_URL = "http://127.0.0.1:9119/api/sidecar/events"
_turn_counts = {}
_turn_counts_lock = threading.Lock()
_TIMEOUT = 5  # seconds – keep it short so we never block the main thread


def report_turn_event(
    *,
    user_message: str,
    agent_response: str,
    tool_events: list,
    session_id: str = "",
    user_id: str = "",
    turn_number: int = None,
    source: str = "your-personal-assistant",
):
    """Build the event payload and POST it in a background thread.

    Parameters match the ``company_agent_turn`` schema.
    """
    from config import conf

    url = conf().get("event_report_url", _DEFAULT_URL)
    if not conf().get("event_report_enabled", True):
        return

    normalized_session_id = _normalize_session_id(session_id)
    if turn_number is None:
        turn_number = _next_turn_number(normalized_session_id)

    payload = {
        "schema_version": 1,
        "event_type": "company_agent_turn",
        "turn_id": f"turn-{uuid.uuid4().hex}",
        "session_id": normalized_session_id,
        "user_id": user_id or conf().get("event_report_user_id", "your-name"),
        "turn_number": turn_number,
        "user_message": user_message,
        "agent_response": agent_response,
        "tool_events": tool_events or [],
        "metadata": {
            "source": conf().get("event_report_source", source),
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
    }

    threading.Thread(
        target=_post_event,
        args=(url, payload),
        daemon=True,
        name="turn-event-reporter",
    ).start()


def _normalize_session_id(session_id: str) -> str:
    session_id = str(session_id or "unknown")
    if session_id.startswith("session-"):
        return session_id
    return f"session-{session_id}"


def _next_turn_number(session_id: str) -> int:
    with _turn_counts_lock:
        _turn_counts[session_id] = _turn_counts.get(session_id, 0) + 1
        return _turn_counts[session_id]


def _post_event(url: str, payload: dict):
    """POST the payload; never raises."""
    try:
        resp = requests.post(
            url,
            json=payload,
            timeout=_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code >= 400:
            logger.warning(
                f"[TurnEventReporter] HTTP {resp.status_code} from {url}: "
                f"{resp.text[:200]}"
            )
        else:
            logger.debug(f"[TurnEventReporter] Reported turn event to {url}")
    except requests.exceptions.ConnectionError:
        logger.debug(
            f"[TurnEventReporter] Could not connect to {url} (endpoint may not be running)"
        )
    except Exception as e:
        logger.warning(f"[TurnEventReporter] Failed to report event: {e}")
