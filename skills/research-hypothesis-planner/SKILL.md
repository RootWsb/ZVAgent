---
name: research-hypothesis-planner
description: Scientific research planning workflow for turning rough ideas into research questions, hypotheses, variables, baselines, datasets, evaluation metrics, ablation plans, feasibility checks, novelty positioning, and reading plans. Use when the user has an early-stage research idea, wants to choose a thesis direction, design a study, prepare a proposal, or convert a paper inspiration into testable experiments.
---

# Research Hypothesis Planner

## Overview

Use this skill before deep reading or coding when the user has an idea but not yet a crisp research question. Turn curiosity into a falsifiable study plan.

Prefer Chinese unless the user asks otherwise. Use `paper-lookup` or `literature-review` when novelty and related work need verification.

## Workflow

1. Restate the idea in one sentence.
2. Define the target problem, data or population, task boundary, and expected contribution.
3. Convert the idea into 2-4 research questions.
4. For each question, write a testable hypothesis and a refutation signal.
5. Identify baselines, datasets, metrics, constraints, and a minimum viable experiment.
6. Separate novelty claims from engineering usefulness.
7. Plan risks: data availability, compute, leakage, confounders, reproducibility, and ethics or safety.
8. End with a reading structure and the first experiment checklist.

## Output Shape

```markdown
# Research Plan: <topic>

## Core Idea
...

## Research Questions
1. ...

## Hypotheses
| Hypothesis | Baseline | Metric | Refutation Signal |
|---|---|---|---|

## Minimum Viable Experiment
- Data:
- Method:
- Baselines:
- Metrics:
- Compute/time:

## Risks And Confounders
- ...

## Reading Plan
- Background:
- Strong baseline:
- Recent related work:

## Next Actions
1. ...
```

Use `experiment-design-reviewer` once the experiment protocol is concrete.
