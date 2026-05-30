#!/usr/bin/env python3
"""List trusted sources from the source registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parents[1]
SOURCES_PATH = BASE_DIR / "references" / "sources.json"


def load_sources() -> Dict[str, List[Dict[str, Any]]]:
    return json.loads(SOURCES_PATH.read_text(encoding="utf-8"))


def filter_sources(
    registry: Dict[str, List[Dict[str, Any]]],
    domain: str | None,
    purpose: str | None,
    primary_only: bool,
) -> Dict[str, List[Dict[str, Any]]]:
    domains = [domain] if domain else sorted(registry)
    result: Dict[str, List[Dict[str, Any]]] = {}

    for name in domains:
        if name not in registry:
            raise ValueError(f"unknown domain: {name}")
        entries = []
        for item in registry[name]:
            if primary_only and item.get("type") != "primary":
                continue
            if purpose and purpose not in item.get("purposes", []):
                continue
            entries.append(item)
        result[name] = entries
    return result


def render_markdown(result: Dict[str, List[Dict[str, Any]]]) -> str:
    parts = ["# Source Registry\n"]
    for domain, entries in result.items():
        parts.append(f"## {domain}\n")
        if not entries:
            parts.append("- No matching sources.\n")
            continue
        for item in entries:
            purposes = ", ".join(item.get("purposes", []))
            parts.append(
                f"- [{item['name']}]({item['url']})"
                f" — {item.get('type', 'unknown')}; {purposes}. {item.get('notes', '')}"
            )
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", choices=["ai-tech", "crypto", "economics", "research", "cross-domain"])
    parser.add_argument("--purpose", help="Filter by purpose tag, e.g. macro-data, market-data, papers, repos")
    parser.add_argument("--primary-only", action="store_true", help="Only include primary/official sources")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    registry = load_sources()
    result = filter_sources(registry, args.domain, args.purpose, args.primary_only)

    if args.format == "markdown":
        print(render_markdown(result), end="")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
