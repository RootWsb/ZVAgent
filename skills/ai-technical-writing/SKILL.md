---
name: ai-technical-writing
description: AI technical writing workflow for model release notes, repository summaries, RAG or agent architecture explainers, benchmark writeups, paper-to-engineering briefs, implementation guides, migration notes, and developer-facing AI articles. Use when the user asks to explain an AI technical topic clearly, turn notes into an AI engineering article, write a model or repo analysis, polish a technical blog, or make AI architecture and evaluation text more precise.
---

# AI Technical Writing

## Overview

Use this skill to write AI technical content that is accurate, concrete, and useful to builders. Prefer mechanism and engineering implications over hype.

Prefer Chinese unless the user asks otherwise. Use `ai-tech-digest`, `ai-benchmark-auditor`, `ai-open-source-evaluator`, or `research-assistant` for upstream analysis.

## Workflow

1. Define the audience: beginner, engineer, researcher, product builder, or decision maker.
2. State the technical thesis in one sentence.
3. Explain mechanism before results: architecture, data, training objective, inference path, tool use, retrieval, evaluation, or deployment.
4. Compare against a familiar baseline.
5. Separate official claims, measured evidence, and your own inference.
6. Include implementation impact: dependencies, latency, cost, reliability, evals, migration, or failure modes.
7. End with what to try next or what to verify.

## Output Shape

```markdown
# <AI Technical Topic>

## TL;DR
...

## What Changed
...

## How It Works
...

## Why It Matters
- Research:
- Engineering:
- Product:

## Evidence Quality
...

## Implementation Notes
- ...

## Open Questions
- ...
```

Avoid calling something SOTA unless the evidence and benchmark context are explicit.
