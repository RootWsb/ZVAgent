#!/usr/bin/env python3
"""Scan and optimize a ZVAgent knowledge directory."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


DOMAIN_DIRS = {"research", "crypto", "economics", "ai-tech", "cross-domain", "profile"}
SKIP_DIRS = {"_meta", ".git", "__pycache__"}
LARGE_BYTES = 12_000


@dataclass
class Page:
    rel: str
    domain: str
    title: str
    bytes: int
    lines: int
    modified: str
    source: str
    summary: str
    headings: list[str]


def workspace_path(raw: str | None) -> Path:
    value = raw or os.environ.get("ZV_AGENT_WORKSPACE") or "~/zvagent"
    return Path(value).expanduser().resolve()


def knowledge_dir(workspace: Path) -> Path:
    return workspace / "knowledge"


def meta_dir(workspace: Path) -> Path:
    return knowledge_dir(workspace) / "_meta"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def append_once(path: Path, line: str) -> None:
    content = read_text(path) if path.exists() else ""
    if line in content:
        return
    with path.open("a", encoding="utf-8", newline="\n") as f:
        if content and not content.endswith("\n"):
            f.write("\n")
        f.write(line.rstrip() + "\n")


def init(workspace: Path) -> None:
    kdir = knowledge_dir(workspace)
    (meta_dir(workspace) / "domain_summaries").mkdir(parents=True, exist_ok=True)
    if not (kdir / "index.md").exists():
        write_text(kdir / "index.md", "# Knowledge Index\n")
    if not (kdir / "log.md").exists():
        write_text(kdir / "log.md", "# Knowledge Log\n")
    today = dt.date.today().isoformat()
    append_once(kdir / "log.md", f"## [{today}] maintain | knowledge compression metadata initialized")


def iter_markdown(kdir: Path) -> Iterable[Path]:
    if not kdir.exists():
        return []
    for path in sorted(kdir.rglob("*.md")):
        rel_parts = path.relative_to(kdir).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        if path.name.lower() in {"index.md", "log.md"}:
            continue
        yield path


def domain_for(path: Path, kdir: Path) -> str:
    rel = path.relative_to(kdir)
    first = rel.parts[0] if rel.parts else "uncategorized"
    return first if first in DOMAIN_DIRS else "uncategorized"


def first_match(pattern: str, text: str) -> str:
    match = re.search(pattern, text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def first_summary(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("> Source:"):
            continue
        if stripped.startswith("- "):
            return stripped[2:180]
        return stripped[:180]
    return ""


def page_from_path(path: Path, kdir: Path) -> Page:
    text = read_text(path)
    stat = path.stat()
    headings = [m.group(1).strip() for m in re.finditer(r"^#{2,3}\s+(.+)$", text, re.MULTILINE)]
    title = first_match(r"^#\s+(.+)$", text) or path.stem.replace("-", " ").title()
    source = first_match(r"^>\s*Source:\s*(.+)$", text)
    return Page(
        rel=str(path.relative_to(kdir)).replace("\\", "/"),
        domain=domain_for(path, kdir),
        title=title,
        bytes=stat.st_size,
        lines=text.count("\n") + 1,
        modified=dt.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
        source=source,
        summary=first_summary(text),
        headings=headings[:8],
    )


def collect_pages(workspace: Path) -> list[Page]:
    kdir = knowledge_dir(workspace)
    return [page_from_path(path, kdir) for path in iter_markdown(kdir)]


def indexed_paths(workspace: Path) -> set[str]:
    index = knowledge_dir(workspace) / "index.md"
    if not index.exists():
        return set()
    text = read_text(index)
    return {m.group(1).strip() for m in re.finditer(r"\]\(([^)]+)\)", text)}


def token_words(value: str) -> set[str]:
    words = re.findall(r"[A-Za-z0-9\u4e00-\u9fff]{2,}", value.lower())
    return {w for w in words if len(w) >= 2}


def duplicate_candidates(pages: list[Page]) -> list[tuple[Page, Page, float]]:
    pairs = []
    for i, left in enumerate(pages):
        left_words = token_words(left.title + " " + left.summary)
        if not left_words:
            continue
        for right in pages[i + 1:]:
            if left.domain != right.domain:
                continue
            right_words = token_words(right.title + " " + right.summary)
            if not right_words:
                continue
            score = len(left_words & right_words) / max(1, len(left_words | right_words))
            same_slug = Path(left.rel).stem == Path(right.rel).stem
            if score >= 0.45 or same_slug:
                pairs.append((left, right, score))
    return sorted(pairs, key=lambda item: item[2], reverse=True)


def scan(workspace: Path, output_format: str) -> None:
    pages = collect_pages(workspace)
    indexed = indexed_paths(workspace)
    unindexed = [p for p in pages if p.rel not in indexed]
    by_domain = Counter(p.domain for p in pages)
    total_bytes = sum(p.bytes for p in pages)
    large = [p for p in pages if p.bytes >= LARGE_BYTES]
    dupes = duplicate_candidates(pages)[:20]
    payload = {
        "page_count": len(pages),
        "total_bytes": total_bytes,
        "domains": dict(sorted(by_domain.items())),
        "large_pages": [asdict(p) for p in large],
        "unindexed_pages": [p.rel for p in unindexed],
        "duplicate_candidates": [
            {"left": a.rel, "right": b.rel, "score": round(score, 3)} for a, b, score in dupes
        ],
    }
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print("# Knowledge Health Scan\n")
    print(f"- Pages: {payload['page_count']}")
    print(f"- Total bytes: {payload['total_bytes']}")
    print("- Domains: " + ", ".join(f"{k}={v}" for k, v in payload["domains"].items()))
    print(f"- Large pages: {len(large)}")
    print(f"- Unindexed pages: {len(unindexed)}")
    print(f"- Duplicate candidates: {len(dupes)}")
    if large:
        print("\n## Large Pages")
        for p in large[:20]:
            print(f"- [{p.title}]({p.rel}) - {p.bytes} bytes")
    if unindexed:
        print("\n## Unindexed Pages")
        for page in unindexed[:40]:
            print(f"- {page.rel}")
    if dupes:
        print("\n## Duplicate Candidates")
        for a, b, score in dupes[:20]:
            print(f"- {score:.2f}: [{a.title}]({a.rel}) <-> [{b.title}]({b.rel})")


def build_map(workspace: Path) -> None:
    init(workspace)
    pages = collect_pages(workspace)
    by_domain: dict[str, list[Page]] = defaultdict(list)
    for page in pages:
        by_domain[page.domain].append(page)
    lines = [
        "# Knowledge Map",
        "",
        f"> Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Use this map to choose a small reading set before opening full notes.",
        "",
    ]
    for domain in sorted(by_domain):
        lines.append(f"## {domain}")
        for page in sorted(by_domain[domain], key=lambda p: p.modified, reverse=True):
            summary = f" - {page.summary}" if page.summary else ""
            lines.append(f"- [{page.title}](../{page.rel}){summary}")
        lines.append("")
    target = meta_dir(workspace) / "knowledge_map.md"
    write_text(target, "\n".join(lines).rstrip() + "\n")
    print(f"Wrote {target}")


def plan(workspace: Path, domain: str | None) -> None:
    init(workspace)
    pages = collect_pages(workspace)
    if domain and domain != "all":
        pages = [p for p in pages if p.domain == domain]
    indexed = indexed_paths(workspace)
    large = [p for p in pages if p.bytes >= LARGE_BYTES]
    unindexed = [p for p in pages if p.rel not in indexed]
    dupes = duplicate_candidates(pages)[:20]
    lines = [
        "# Compaction Plan",
        "",
        f"> Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> Scope: {domain or 'all'}",
        "",
        "## Priorities",
        "",
        "1. Add missing index entries.",
        "2. Summarize large pages into domain summaries while preserving original links.",
        "3. Merge duplicate candidates only after reading both pages.",
        "4. Keep citations, dates, assumptions, and risk framing.",
        "",
    ]
    lines.append("## Missing Index Entries")
    if unindexed:
        for p in unindexed[:80]:
            lines.append(f"- [ ] Add [{p.title}]({p.rel}) - {p.summary or 'summary needed'}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Large Pages To Summarize")
    if large:
        for p in large[:80]:
            lines.append(f"- [ ] [{p.title}]({p.rel}) - {p.bytes} bytes, {p.lines} lines")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Duplicate Candidates")
    if dupes:
        for a, b, score in dupes:
            lines.append(f"- [ ] {score:.2f}: [{a.title}]({a.rel}) <-> [{b.title}]({b.rel})")
    else:
        lines.append("- None")
    lines.append("")
    target = meta_dir(workspace) / "compaction_plan.md"
    write_text(target, "\n".join(lines))
    print(f"Wrote {target}")


def score_page(page: Page, query_words: set[str], domain: str | None) -> float:
    words = token_words(page.title + " " + page.summary + " " + " ".join(page.headings))
    score = len(words & query_words)
    if domain and page.domain == domain:
        score += 2
    if page.source:
        score += 0.25
    score += min(page.bytes, LARGE_BYTES) / LARGE_BYTES * 0.15
    return score


def context(workspace: Path, query: str, domain: str | None, max_files: int) -> None:
    pages = collect_pages(workspace)
    if domain and domain != "all":
        pages = [p for p in pages if p.domain == domain]
    query_words = token_words(query)
    ranked = sorted(pages, key=lambda p: score_page(p, query_words, domain), reverse=True)
    print("# Knowledge Context Pack\n")
    print(f"- Query: {query}")
    print(f"- Domain: {domain or 'all'}")
    print(f"- Selected files: {min(max_files, len(ranked))}\n")
    for page in ranked[:max_files]:
        print(f"## {page.title}")
        print(f"- Path: knowledge/{page.rel}")
        print(f"- Domain: {page.domain}")
        if page.summary:
            print(f"- Summary: {page.summary}")
        if page.source:
            print(f"- Source: {page.source}")
        if page.headings:
            print("- Headings: " + "; ".join(page.headings[:6]))
        print("")


def main() -> None:
    parser = argparse.ArgumentParser(description="Optimize ZVAgent knowledge maps and compaction plans")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("--workspace")

    p_scan = sub.add_parser("scan")
    p_scan.add_argument("--workspace")
    p_scan.add_argument("--format", choices=["markdown", "json"], default="markdown")

    p_map = sub.add_parser("build-map")
    p_map.add_argument("--workspace")

    p_plan = sub.add_parser("plan")
    p_plan.add_argument("--workspace")
    p_plan.add_argument("--domain", default="all")

    p_context = sub.add_parser("context")
    p_context.add_argument("--workspace")
    p_context.add_argument("--query", required=True)
    p_context.add_argument("--domain", default="all")
    p_context.add_argument("--max-files", type=int, default=5)

    args = parser.parse_args()
    workspace = workspace_path(getattr(args, "workspace", None))
    if args.cmd == "init":
        init(workspace)
        print(f"Initialized knowledge metadata under {meta_dir(workspace)}")
    elif args.cmd == "scan":
        scan(workspace, args.format)
    elif args.cmd == "build-map":
        build_map(workspace)
    elif args.cmd == "plan":
        plan(workspace, args.domain)
    elif args.cmd == "context":
        context(workspace, args.query, args.domain, args.max_files)


if __name__ == "__main__":
    main()
