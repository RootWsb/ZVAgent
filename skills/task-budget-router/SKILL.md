---
name: task-budget-router
description: Choose the smallest effective execution plan for a user request by routing domain, selecting quick/brief/deep/archive mode, setting retrieval and source budgets, and recommending skills. Use before substantial analysis, recurring briefs, current-data questions, knowledge-base answers, or whenever the user asks to save tokens, shorten answers, go deeper, archive results, or control research depth.
---

# Task Budget Router

Use this skill as the first planning layer for non-trivial work. It turns a request into a compact budget so the assistant does not over-read, over-search, or over-write.

## Budget Contract

Produce or follow this plan:

```markdown
Domain: <research|crypto|economics|ai-tech|cross-domain|general>
Mode: <quick|brief|deep|archive>
Primary skills: <skill names>
Local knowledge budget: <N pages>
Fresh source budget: <N sources>
Output budget: <target length>
Archive: <yes|no>
Quality gate: <yes|no>
```

Use `scripts/route_task.py` for deterministic routing:

```bash
python skills/task-budget-router/scripts/route_task.py --prompt "<user request>" --format markdown
```

For machine-readable output:

```bash
python skills/task-budget-router/scripts/route_task.py --prompt "<user request>" --format json
```

## Defaults

| Mode | Trigger | Local pages | Fresh sources | Output budget |
|---|---|---:|---:|---|
| `quick` | simple question, "short", "TL;DR" | 0-1 | 0-2 | <= 300 Chinese chars or 5 bullets |
| `brief` | normal analysis | 1-3 | 2-4 | 600-1200 Chinese chars |
| `deep` | "deep", "systematic", comparison, reproduction, strategy | 3-8 | 4-8 | structured long answer |
| `archive` | save, archive, durable note, scheduled brief | 3-8 | 4-8 | concise Markdown suitable for `knowledge/` |

Prefer `brief` when no signal is clear.

## Routing Rules

- Research: papers, arXiv, literature, formulas, reproduction, experiments.
- Crypto: BTC, ETH, token, DeFi, on-chain, exchange, wallet, regulation, crypto market.
- Economics: CPI, GDP, jobs, inflation, rates, Fed, central bank, fiscal, FX, commodities.
- AI Tech: model releases, RAG, Agent, inference, training, benchmarks, GitHub AI projects.
- Cross-domain: two or more domains interact.

## Skill Selection

- Research: `research-assistant`, optionally `paper-lookup`, `literature-review`, `citation-management`.
- Crypto: `crypto-news`, optionally `surf`.
- Economics: `economic-analysis`, optionally `usfiscaldata`, `statistical-analysis`.
- AI Tech: `ai-tech-digest`, optionally `huggingface-papers`, `huggingface-datasets`.
- Large local knowledge: `knowledge-compression-indexer`.
- User preferences or feedback: `usage-learning-optimizer`, then `feedback-template-evolver` when future behavior should change.
- Archive durable output: `knowledge-wiki`.
- Publish or schedule important briefs: `quality-guardrails`.

## Current Data Policy

If the request says "latest", "today", "yesterday", "this week", "price", "ranking", "release", "policy", "API", "regulation", or asks for market/news analysis, allocate fresh sources and use `source-registry` first.

## Execution Discipline

- Start with the smallest budget that can answer the question.
- Expand only when evidence is missing or the user asks for depth.
- Use local profile/context before reading many old notes.
- Turn stable user feedback into proposals with `feedback-template-evolver`.
- Use `knowledge-compression-indexer` for large local knowledge answers.
- Do not archive unless the user asks, the result is durable, or the task is a scheduled brief.
- For crypto/finance, include risk framing and avoid deterministic buy/sell instructions.
