#!/usr/bin/env python3
"""Manage a crypto watchlist JSON file for market briefs and risk radar."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_WATCHLIST = {
    "version": 1,
    "updated_at": "",
    "settings": {
        "currency": "usd",
        "price_24h_alert_pct": 5,
        "price_7d_alert_pct": 10,
        "tvl_7d_alert_pct": 10,
        "volume_to_mcap_min": 0.02,
        "chain_concentration_alert_pct": 80,
    },
    "assets": [],
}


def expand_path(path: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(path))).resolve()


def default_watchlist_path(workspace: str) -> Path:
    return expand_path(workspace) / "knowledge" / "crypto" / "watchlist.json"


def load_watchlist(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return json.loads(json.dumps(DEFAULT_WATCHLIST))
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("watchlist must be a JSON object")
    data.setdefault("version", 1)
    data.setdefault("settings", {})
    data.setdefault("assets", [])
    if not isinstance(data["assets"], list):
        raise ValueError("watchlist.assets must be a list")
    merged_settings = dict(DEFAULT_WATCHLIST["settings"])
    merged_settings.update(data.get("settings") or {})
    data["settings"] = merged_settings
    return data


def save_watchlist(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def item_key(item: Dict[str, Any]) -> str:
    kind = item.get("type")
    if kind == "coin":
        return f"coin:{item.get('id', '').lower()}"
    if kind == "protocol":
        return f"protocol:{item.get('slug', '').lower()}"
    return f"{kind}:{item.get('id') or item.get('slug') or item.get('name')}"


def upsert_asset(data: Dict[str, Any], item: Dict[str, Any]) -> str:
    target_key = item_key(item)
    assets: List[Dict[str, Any]] = data["assets"]
    for index, existing in enumerate(assets):
        if item_key(existing) == target_key:
            merged = dict(existing)
            merged.update({key: value for key, value in item.items() if value not in (None, "", [])})
            assets[index] = merged
            return "updated"
    assets.append(item)
    return "added"


def remove_asset(data: Dict[str, Any], key: str) -> bool:
    key = key.lower()
    assets = data["assets"]
    kept = [
        item for item in assets
        if key not in {
            str(item.get("id", "")).lower(),
            str(item.get("slug", "")).lower(),
            str(item.get("symbol", "")).lower(),
            str(item.get("name", "")).lower(),
            item_key(item).lower(),
        }
    ]
    data["assets"] = kept
    return len(kept) != len(assets)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default="~/zvagent", help="ZVAgent workspace path.")
    parser.add_argument("--path", help="Explicit watchlist JSON path.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    subparsers.add_parser("init", help="Create an empty watchlist if missing.")
    subparsers.add_parser("list", help="Print the watchlist JSON.")

    coin = subparsers.add_parser("add-coin", help="Add or update a CoinGecko coin.")
    coin.add_argument("--id", required=True, help="CoinGecko id, e.g. bitcoin.")
    coin.add_argument("--symbol", default="", help="Ticker symbol, e.g. BTC.")
    coin.add_argument("--name", default="", help="Display name.")
    coin.add_argument("--notes", default="", help="Research notes.")
    coin.add_argument("--tags", default="", help="Comma-separated risk/theme tags.")

    protocol = subparsers.add_parser("add-protocol", help="Add or update a DefiLlama protocol.")
    protocol.add_argument("--slug", required=True, help="DefiLlama slug, e.g. lido.")
    protocol.add_argument("--name", default="", help="Display name.")
    protocol.add_argument("--notes", default="", help="Research notes.")
    protocol.add_argument("--tags", default="", help="Comma-separated risk/theme tags.")

    remove = subparsers.add_parser("remove", help="Remove by id, symbol, slug, or name.")
    remove.add_argument("key")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = expand_path(args.path) if args.path else default_watchlist_path(args.workspace)
    data = load_watchlist(path)

    if args.action == "init":
        save_watchlist(path, data)
        print(json.dumps({"status": "success", "path": str(path), "assets": len(data["assets"])}, ensure_ascii=False))
        return

    if args.action == "list":
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if args.action == "add-coin":
        status = upsert_asset(data, {
            "type": "coin",
            "id": args.id,
            "symbol": args.symbol.upper() if args.symbol else "",
            "name": args.name,
            "notes": args.notes,
            "tags": [tag.strip() for tag in args.tags.split(",") if tag.strip()],
        })
        save_watchlist(path, data)
        print(json.dumps({"status": status, "path": str(path), "asset": args.id}, ensure_ascii=False))
        return

    if args.action == "add-protocol":
        status = upsert_asset(data, {
            "type": "protocol",
            "slug": args.slug,
            "name": args.name,
            "notes": args.notes,
            "tags": [tag.strip() for tag in args.tags.split(",") if tag.strip()],
        })
        save_watchlist(path, data)
        print(json.dumps({"status": status, "path": str(path), "asset": args.slug}, ensure_ascii=False))
        return

    if args.action == "remove":
        removed = remove_asset(data, args.key)
        save_watchlist(path, data)
        print(json.dumps({"status": "success", "removed": removed, "path": str(path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
