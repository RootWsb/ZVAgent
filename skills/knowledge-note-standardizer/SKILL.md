---
name: knowledge-note-standardizer
description: Knowledge-base writing standardization workflow for durable notes, research summaries, source digests, local wiki pages, cross-links, tags, filenames, changelog entries, and concise reusable context packs. Use when the user asks to save knowledge, clean up notes, normalize Markdown pages, archive a result, turn messy material into a knowledge-base entry, add tags and backlinks, or standardize notes across research, crypto, AI technology, economics, and financial analysis.
---

# Knowledge Note Standardizer

## Overview

Use this skill to turn useful output into a durable local knowledge page. Keep notes compact, source-aware, and easy to retrieve later.

Prefer `knowledge-wiki` for actual knowledge-base writes and index/log updates. This skill defines the writing standard.

## Workflow

1. Decide whether the content is durable enough to save. Do not archive transient noise unless it supports a recurring workflow.
2. Choose the domain folder: `knowledge/research/`, `knowledge/crypto/`, `knowledge/ai-tech/`, `knowledge/economics/`, or `knowledge/cross-domain/`.
3. Create a clear title and lowercase kebab-case filename for English names. Use clear Chinese filenames only when the project already uses them.
4. Preserve sources, local file paths, dates, dataset periods, and uncertainty.
5. Add tags and backlinks to related local notes when known.
6. Keep the note short enough to be reused in future prompts.
7. Update `knowledge/index.md` and `knowledge/log.md` through `knowledge-wiki` after writing.

## Note Shape

```markdown
# <Title>

> Updated: <YYYY-MM-DD>
> Tags: #domain #topic #status

## Summary
...

## Key Points
- ...

## Evidence / Sources
- ...

## Implications
- ...

## Open Questions
- ...

## Related Notes
- ...
```

## Compression Rule

If a note is becoming long, split it into:

- a short index/summary page;
- detailed source notes under a subfolder;
- links instead of repeated text.
