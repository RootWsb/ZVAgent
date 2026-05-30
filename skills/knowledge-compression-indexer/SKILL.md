---
name: knowledge-compression-indexer
description: Optimize the workspace knowledge base for lower token usage by scanning knowledge pages, building lightweight maps, detecting duplicate or oversized notes, generating compaction plans, and producing small context packs. Use when the user asks to compress knowledge, reduce token use, optimize indexes, clean up notes, deduplicate knowledge, summarize accumulated notes, or before answering from a large knowledge base.
---

# Knowledge Compression Indexer

Use this skill to keep `knowledge/` useful as it grows.

## Goal

Make the assistant read less while knowing more:

- keep `knowledge/index.md` concise
- maintain lightweight maps under `knowledge/_meta/`
- detect large, stale, duplicate, or unindexed pages
- create domain summaries that point to original pages
- build small context packs before answering from many notes

This skill plans and scaffolds compaction. Use `knowledge-wiki` for final knowledge-page edits when writing human-quality summaries.

## Files

Generated metadata lives under:

- `knowledge/_meta/knowledge_map.md`
- `knowledge/_meta/compaction_plan.md`
- `knowledge/_meta/domain_summaries/<domain>.md`

These files are indexes, not source-of-truth analysis. Keep source notes in their domain folders.

## Core Commands

Initialize metadata folders:

```bash
python skills/knowledge-compression-indexer/scripts/optimize_knowledge.py init --workspace .
```

Scan knowledge health:

```bash
python skills/knowledge-compression-indexer/scripts/optimize_knowledge.py scan --workspace . --format markdown
```

Build lightweight map:

```bash
python skills/knowledge-compression-indexer/scripts/optimize_knowledge.py build-map --workspace .
```

Create compaction plan:

```bash
python skills/knowledge-compression-indexer/scripts/optimize_knowledge.py plan --workspace . --domain ai-tech
```

Build a small context pack:

```bash
python skills/knowledge-compression-indexer/scripts/optimize_knowledge.py context --workspace . --query "RAG 评测" --domain ai-tech --max-files 5
```

## Compression Workflow

1. Run `scan` to understand size, domains, unindexed files, and large notes.
2. Run `plan` for the target domain.
3. Read only the listed candidate files, not the whole knowledge base.
4. Create or update a domain summary under `knowledge/_meta/domain_summaries/`.
5. If two notes duplicate the same durable idea, merge the shorter insight into the better page and keep links.
6. Update `knowledge/index.md` and `knowledge/log.md` via `knowledge-wiki`.

## Compression Rules

- Do not delete source pages automatically.
- Never compress away citations, source URLs, dates, assumptions, or risk framing.
- Preserve links to original notes.
- Prefer one domain summary page over many repeated explanations.
- Keep index lines one sentence long.
- Use `context` output as a reading shortlist before answering.

## When Answering From Existing Knowledge

If the domain has many notes:

1. Read `knowledge/_meta/knowledge_map.md` if present.
2. Run or use `context` to choose a small subset.
3. Read at most the chosen files plus any required source pages.
4. Answer with links to local pages instead of restating every detail.

