#!/usr/bin/env python3
"""Create a standardized vertical research brief draft.

The script is intentionally conservative: it does not fetch live data. It turns
already gathered source notes into a consistent Markdown shell and can
optionally archive it into a workspace knowledge base.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List


DOMAIN_FOLDERS = {
    "ai-tech": ("ai-tech/digests", "AI Tech"),
    "crypto": ("crypto/briefs", "Crypto"),
    "economics": ("economics/macro-briefs", "Economics"),
    "research": ("research/experiments", "Research"),
    "cross-domain": ("cross-domain", "Cross Domain"),
}

CADENCE_LABELS = {
    "daily": "Daily",
    "weekly": "Weekly",
    "monthly": "Monthly",
    "ad-hoc": "Ad Hoc",
}


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "brief"


def load_sources(path: str | None) -> List[Dict[str, Any]]:
    if not path:
        return []
    source_path = Path(path)
    data = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("--sources-json must contain a JSON array")
    normalized = []
    for item in data:
        if isinstance(item, dict):
            normalized.append(item)
        else:
            normalized.append({"title": str(item)})
    return normalized


def render_sources(sources: List[Dict[str, Any]]) -> str:
    if not sources:
        return "- Pending source verification.\n"

    lines = []
    for source in sources:
        title = source.get("title") or source.get("name") or "Untitled source"
        url = source.get("url")
        note = source.get("note") or source.get("summary") or ""
        if url:
            line = f"- [{title}]({url})"
        else:
            line = f"- {title}"
        if note:
            line += f" — {note}"
        lines.append(line)
    return "\n".join(lines) + "\n"


def build_markdown(args: argparse.Namespace, sources: List[Dict[str, Any]]) -> str:
    folder, domain_label = DOMAIN_FOLDERS[args.domain]
    cadence_label = CADENCE_LABELS[args.cadence]
    title = args.topic or f"{domain_label} {cadence_label} Brief"

    return f"""# {args.date} {title}

> Source: automated {args.cadence} brief draft. Domain: {args.domain}. Generated: {datetime.now().isoformat(timespec="seconds")}.

## 结论

- Pending synthesis.

## 依据

{render_sources(sources)}
## 机制

- Pending mechanism analysis.

## 风险/不确定性

- Pending risk review.

## 下一步

- Verify current facts before publishing.
- Add durable findings to related knowledge pages when useful.

## Metadata

- Domain: {args.domain}
- Cadence: {args.cadence}
- Folder: knowledge/{folder}/
"""


def update_index(knowledge_dir: Path, rel_path: str, title: str, domain_label: str) -> None:
    index_path = knowledge_dir / "index.md"
    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
    else:
        content = "# Knowledge Index\n"

    line = f"- [{title}]({rel_path}) — {domain_label} automated brief draft"
    if line in content:
        return

    heading = f"## {domain_label}"
    if heading in content:
        content = content.replace(heading, f"{heading}\n\n{line}", 1)
    else:
        if not content.endswith("\n"):
            content += "\n"
        content += f"\n{heading}\n\n{line}\n"
    index_path.write_text(content, encoding="utf-8")


def append_log(knowledge_dir: Path, title: str) -> None:
    log_path = knowledge_dir / "log.md"
    line = f"## [{date.today().isoformat()}] synthesize | {title}\n"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line)


def write_brief(args: argparse.Namespace, markdown: str) -> Path:
    if not args.workspace:
        raise ValueError("--workspace is required with --write")

    folder, domain_label = DOMAIN_FOLDERS[args.domain]
    knowledge_dir = Path(args.workspace).expanduser() / "knowledge"
    target_dir = knowledge_dir / folder
    target_dir.mkdir(parents=True, exist_ok=True)

    title = args.topic or f"{domain_label} {CADENCE_LABELS[args.cadence]} Brief"
    filename = f"{args.date}-{slugify(title)}.md"
    target = target_dir / filename
    target.write_text(markdown, encoding="utf-8")

    rel_path = str(target.relative_to(knowledge_dir)).replace("\\", "/")
    update_index(knowledge_dir, rel_path, f"{args.date} {title}", domain_label)
    append_log(knowledge_dir, f"{args.date} {title}")
    return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", help="Agent workspace path")
    parser.add_argument("--domain", required=True, choices=sorted(DOMAIN_FOLDERS))
    parser.add_argument("--cadence", default="daily", choices=sorted(CADENCE_LABELS))
    parser.add_argument("--topic", default="")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--sources-json", help="JSON array of source objects")
    parser.add_argument("--write", action="store_true", help="Write into workspace knowledge base")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sources = load_sources(args.sources_json)
    markdown = build_markdown(args, sources)

    if args.write:
        target = write_brief(args, markdown)
        print(json.dumps({"status": "success", "path": str(target)}, ensure_ascii=False))
    else:
        print(markdown)


if __name__ == "__main__":
    main()
