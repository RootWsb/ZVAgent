---
name: ai-open-source-evaluator
description: AI open-source repository evaluation workflow for GitHub projects, model repos, agent frameworks, RAG libraries, inference tools, training code, demos, and reproducibility claims. Use when the user asks whether an AI repo is worth adopting, reproducing, deploying, comparing with alternatives, or tracking as a technical project.
---

# AI Open Source Evaluator

## Overview

Use this skill to evaluate an AI repository as an engineer: what it does, whether it works, how hard it is to run, and what risks adoption creates.

Prefer Chinese unless the user asks otherwise. Inspect the repository, release notes, docs, and model pages before making maturity claims.

## Workflow

1. Identify the real scope from README, docs, examples, papers, demos, and package metadata.
2. Check repo health: license, recent commits, releases, issues, tests, CI, install path, examples, dependency pins, and supported platforms.
3. Inspect technical substance: core modules, model and data requirements, inference or training path, tool integrations, API surface, and extension points.
4. Check reproducibility: minimal run path, weights, datasets, checkpoints, expected outputs, and benchmark scripts.
5. Check adoption risks: unstable APIs, missing license, hidden costs, security-sensitive tools, abandoned dependencies, vendor lock-in, and unclear data behavior.
6. Compare alternatives when the user asks whether to adopt.
7. End with `try`, `watch`, `avoid`, or `reference-only` and a minimal verification plan.

## Output Shape

```markdown
# AI Repo Evaluation: <repo>

## Verdict
- Recommendation:
- Best use case:
- Biggest risk:

## What It Implements
...

## Maturity
| Area | Status | Evidence |
|---|---|---|

## Reproducibility
- Minimal run:
- Required assets:
- Expected outputs:

## Adoption Risks
- ...

## Verification Plan
1. ...
```
