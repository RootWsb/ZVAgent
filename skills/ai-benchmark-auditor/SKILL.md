---
name: ai-benchmark-auditor
description: AI benchmark and evaluation audit workflow for model claims, leaderboard results, benchmark suites, eval prompts, contamination risk, metric validity, statistical uncertainty, cost and latency tradeoffs, and apples-to-apples comparisons. Use when the user asks whether an AI benchmark, SOTA claim, model comparison, eval report, leaderboard ranking, or benchmark chart is trustworthy.
---

# AI Benchmark Auditor

## Overview

Use this skill to slow down benchmark hype. Check whether the evidence actually supports the claim and whether the comparison is fair enough for a decision.

Prefer Chinese unless the user asks otherwise. Use original model docs, papers, eval repos, and benchmark pages before media summaries.

## Audit Workflow

1. Identify the exact claim: model, benchmark, score, date, source, and comparison set.
2. Find the original evidence: model card, paper, eval repo, leaderboard, API docs, or official release note.
3. Check benchmark fit: tasks, language, domain, difficulty, metric, and relevance to the user's workload.
4. Check fairness: model versions, prompts, tools, retrieval, context, sampling, refusal policy, cost, latency, and inference budget.
5. Check contamination risk: public test sets, data overlap, prompt exposure, benchmark saturation, and synthetic judge failure.
6. Check uncertainty: sample size, variance, confidence intervals, repeated runs, and judge reliability.
7. Translate the result into a next action: trust, test locally, ignore, or run targeted evals.

## Output Shape

```markdown
# Benchmark Audit: <claim>

## Verdict
- Trust level: high / medium / low
- Fit for the user's task:

## Claim And Evidence
...

## Fairness Check
| Dimension | Status | Notes |
|---|---|---|

## Benchmark Fit
...

## Risks
- Contamination:
- Metric weakness:
- Cost/latency blind spot:

## Recommended Local Eval
- ...
```

Use `ai-tech-digest` for broad model release summaries.
