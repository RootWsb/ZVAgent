---
name: evidence-citation-writer
description: Evidence-grounded writing workflow for citations, source-backed claims, fact-versus-inference labeling, quotation discipline, footnotes, reference checks, evidence tables, claim audits, and cautious wording. Use when the user asks to make an analysis more credible, add citations, rewrite with sources, check whether claims are supported, produce evidence-based paragraphs, or standardize source attribution across research, crypto, AI technology, economics, and financial reports.
---

# Evidence Citation Writer

## Overview

Use this skill to make writing auditable. Every important claim should map to a source, a local file path, or a clearly labeled inference.

Prefer primary sources for factual claims. Use `source-registry` before current or evidence-sensitive work and `citation-management` for formal bibliographic metadata.

## Claim Discipline

Label claims when useful:

- `Fact`: directly supported by a cited source.
- `Inference`: reasoned interpretation from facts.
- `Assumption`: scenario condition that may be wrong.
- `Gap`: important claim still lacking evidence.

## Workflow

1. Extract the main claims from the draft.
2. Group claims by evidence type: primary source, structured data, paper, local file, specialist media, or unsupported.
3. Rewrite unsupported or overstrong claims with cautious language.
4. Attach citations close to the claim they support.
5. Avoid long direct quotes. Paraphrase and cite unless a short quote is necessary.
6. Keep source titles, dates, dataset periods, and retrieval dates when recency matters.
7. End with a short evidence-gap list if the writing is not fully supported.

## Output Shape

```markdown
## Revised Evidence-Based Version
...

## Evidence Map
| Claim | Evidence | Confidence | Gap |
|---|---|---|---|

## Wording Changes
- ...

## Evidence Gaps
- ...
```

Do not fabricate citations, URLs, page numbers, or publication metadata.
