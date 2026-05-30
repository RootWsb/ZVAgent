#!/usr/bin/env python3
"""Install a recurring crypto market brief scheduler task.

This script writes a scheduler ``agent_task`` into
``<workspace>/scheduler/tasks.json``. It is useful for configuring a deployed
ZVAgent instance without creating the task from chat.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

try:
    from croniter import croniter
except ImportError:  # pragma: no cover - depends on runtime environment
    croniter = None


DEFAULT_AI_TASK = (
    "Use crypto-news to produce today's crypto market brief in Chinese. "
    "First run the structured brief generator or fetch current structured data "
    "for global market, BTC/ETH, DeFi TVL, stablecoin supply, and stable yield pools. "
    "If knowledge/crypto/watchlist.json exists, include its watchlist risk radar. "
    "Then verify any breaking news, regulation, ETF, exchange, hack, or macro claims "
    "with current sources. Separate facts, inference, and assumptions; include risk "
    "framing and avoid deterministic buy/sell instructions. Archive durable output "
    "under knowledge/crypto/briefs/ and update knowledge/index.md and knowledge/log.md. "
    "Before publishing, use quality-guardrails to validate sources and financial risk framing."
)


def expand_path(path: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(path))).resolve()


def slug_id(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s_-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    return text.strip("_") or "crypto_brief"


def load_store(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"version": 1, "tasks": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid scheduler store JSON: {path}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Scheduler store must be a JSON object: {path}")
    tasks = data.setdefault("tasks", {})
    if not isinstance(tasks, dict):
        raise ValueError("Scheduler store field 'tasks' must be an object")
    data.setdefault("version", 1)
    return data


def save_store(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now().isoformat()
    if path.exists():
        backup = path.with_suffix(path.suffix + ".bak")
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def next_run(cron_expr: str) -> str:
    if croniter is None:
        return ""
    cron = croniter(cron_expr, datetime.now())
    return cron.get_next(datetime).isoformat()


def validate_cron(cron_expr: str) -> None:
    """Validate cron expression with croniter when available, otherwise lightly."""
    if croniter is not None:
        croniter(cron_expr, datetime.now())
        return
    parts = cron_expr.split()
    if len(parts) != 5:
        raise ValueError("Cron expression must have 5 fields")


def build_task(args: argparse.Namespace) -> Dict[str, Any]:
    now = datetime.now().isoformat()
    task_id = args.task_id or ("crypto_daily_brief" if args.name == "加密市场日报" else slug_id(args.name))
    task = {
        "id": task_id,
        "name": args.name,
        "enabled": not args.disabled,
        "created_at": now,
        "updated_at": now,
        "schedule": {
            "type": "cron",
            "expression": args.cron,
        },
        "action": {
            "type": "agent_task",
            "task_description": args.ai_task or DEFAULT_AI_TASK,
            "receiver": args.receiver,
            "receiver_name": args.receiver_name or args.receiver,
            "is_group": bool(args.group),
            "channel_type": args.channel,
            "notify_session_id": args.session_id or args.receiver,
        },
    }
    run_at = next_run(args.cron)
    if run_at:
        task["next_run_at"] = run_at
    return task


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default="~/zvagent", help="Agent workspace path.")
    parser.add_argument("--store-path", help="Explicit scheduler tasks.json path.")
    parser.add_argument("--name", default="加密市场日报", help="Scheduler task name.")
    parser.add_argument("--task-id", help="Stable task id. Defaults to slugified name.")
    parser.add_argument("--cron", default="30 8 * * *", help="Cron expression. Default: daily 08:30.")
    parser.add_argument("--channel", default="web", help="Channel type, e.g. web, weixin:wx1.")
    parser.add_argument("--receiver", help="Receiver/session id for the target channel.")
    parser.add_argument("--receiver-name", default="", help="Human-readable receiver name.")
    parser.add_argument("--session-id", default="", help="Conversation id to remember delivered output under.")
    parser.add_argument("--group", action="store_true", help="Mark receiver as a group chat.")
    parser.add_argument("--ai-task", default="", help="Override default AI task description.")
    parser.add_argument("--disabled", action="store_true", help="Install task disabled.")
    parser.add_argument("--dry-run", action="store_true", help="Print task JSON without writing.")
    parser.add_argument("--replace", action="store_true", help="Replace an existing task with the same id.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.receiver and not args.dry_run:
        raise SystemExit("--receiver is required unless --dry-run is used")

    # Validate early so users get a clear error.
    validate_cron(args.cron)

    if args.dry_run and not args.receiver:
        args.receiver = "<receiver>"

    task = build_task(args)
    if args.dry_run:
        print(json.dumps({"status": "dry-run", "task": task}, ensure_ascii=False, indent=2))
        return

    store_path = expand_path(args.store_path) if args.store_path else expand_path(args.workspace) / "scheduler" / "tasks.json"
    store = load_store(store_path)
    tasks = store["tasks"]
    task_id = task["id"]
    existed = task_id in tasks
    if existed and not args.replace:
        raise SystemExit(f"Task '{task_id}' already exists. Use --replace to update it.")

    if existed:
        task["created_at"] = tasks[task_id].get("created_at", task["created_at"])
    tasks[task_id] = task
    save_store(store_path, store)

    print(json.dumps({
        "status": "success",
        "path": str(store_path),
        "task_id": task_id,
        "replaced": existed,
        "next_run_at": task.get("next_run_at"),
        "croniter_available": croniter is not None,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
