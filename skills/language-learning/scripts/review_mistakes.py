#!/usr/bin/env python3
"""Record and review language-learning mistakes."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List


def mistakes_path(workspace: str | None, explicit_path: str | None = None) -> Path:
    if explicit_path:
        return Path(explicit_path).expanduser()
    if not workspace:
        raise ValueError("--workspace or --mistakes is required")
    return Path(workspace).expanduser() / "knowledge" / "language-learning" / "mistakes.json"


def load_items(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"mistakes file must contain a JSON array: {path}")
    return [item for item in data if isinstance(item, dict)]


def save_items(path: Path, items: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_language(value: str) -> str:
    return (value or "").strip().lower()


def filter_items(items: List[Dict[str, Any]], target_language: str) -> List[Dict[str, Any]]:
    if not target_language:
        return items
    target = normalize_language(target_language)
    return [item for item in items if normalize_language(item.get("target_language", "")) == target]


def add_item(args: argparse.Namespace) -> None:
    path = mistakes_path(args.workspace, args.mistakes)
    items = load_items(path)
    entry = {
        "id": f"mistake-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "target_language": args.target_language,
        "category": args.category,
        "text": args.text,
        "correction": args.correction,
        "note": args.note,
        "source": args.source,
        "review_count": 0,
        "last_reviewed": "",
    }
    items.append(entry)
    save_items(path, items)
    print(json.dumps({"status": "success", "path": str(path), "item": entry}, ensure_ascii=False))


def list_items(args: argparse.Namespace) -> None:
    path = mistakes_path(args.workspace, args.mistakes)
    items = filter_items(load_items(path), args.target_language)
    print(json.dumps({"status": "success", "path": str(path), "items": items}, ensure_ascii=False, indent=2))


def review_items(args: argparse.Namespace) -> None:
    path = mistakes_path(args.workspace, args.mistakes)
    items = filter_items(load_items(path), args.target_language)
    selected = sorted(items, key=lambda item: (item.get("review_count", 0), item.get("created_at", "")))[: args.limit]
    lines = [
        f"# {date.today().isoformat()} Mistake Review",
        "",
        f"> Target language: {args.target_language or 'all'}. Items: {len(selected)}.",
        "",
    ]
    if not selected:
        lines.append("- No saved mistakes yet. Add one after the next correction.")
    for i, item in enumerate(selected, start=1):
        lines.extend([
            f"## Card {i}",
            "",
            f"- Original: `{item.get('text', '')}`",
            f"- Correction: `{item.get('correction', '')}`",
            f"- Note: {item.get('note', '')}",
            "- Task: create one new sentence using the corrected pattern.",
            "",
        ])
        item["review_count"] = int(item.get("review_count", 0) or 0) + 1
        item["last_reviewed"] = datetime.now().isoformat(timespec="seconds")
    if args.mark_reviewed:
        all_items = load_items(path)
        by_id = {item.get("id"): item for item in selected}
        updated = [by_id.get(item.get("id"), item) for item in all_items]
        save_items(path, updated)
    print("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", help="ZVAgent workspace path")
    parser.add_argument("--mistakes", help="Explicit mistakes.json path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", help="Add a correction card")
    add.add_argument("--target-language", default="English")
    add.add_argument("--category", default="grammar")
    add.add_argument("--text", required=True)
    add.add_argument("--correction", required=True)
    add.add_argument("--note", default="")
    add.add_argument("--source", default="chat")
    add.set_defaults(func=add_item)

    review = subparsers.add_parser("review", help="Render review cards")
    review.add_argument("--target-language", default="")
    review.add_argument("--limit", type=int, default=8)
    review.add_argument("--mark-reviewed", action="store_true")
    review.set_defaults(func=review_items)

    list_cmd = subparsers.add_parser("list", help="List saved mistakes as JSON")
    list_cmd.add_argument("--target-language", default="")
    list_cmd.set_defaults(func=list_items)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

