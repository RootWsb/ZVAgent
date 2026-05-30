---
name: experiment-design-reviewer
description: Experiment design review workflow for scientific and AI experiments, including baselines, controls, ablations, metrics, statistical validity, data leakage, reproducibility, compute budget, logging, and interpretation risk. Use when the user has an experiment plan, paper experiment section, training run design, benchmark setup, ablation table, evaluation protocol, or suspicious result that needs methodological review before running or reporting.
---

# Experiment Design Reviewer

## Overview

Use this skill to find design flaws before compute is spent or conclusions are written. It reviews methodology rather than summarizing papers.

Prefer Chinese unless the user asks otherwise. Use `statistical-analysis` when formal tests, effect sizes, power, or assumptions are needed.

## Review Workflow

1. Identify the claim the experiment should support.
2. Check whether dataset, task, split, metric, and baseline match that claim.
3. Look for leakage, benchmark overfitting, duplicate data, hidden post-selection, and confounders.
4. Check baselines: simple baseline, strong baseline, prior work when relevant, and same-budget comparison.
5. Check ablations: removals, replacements, sensitivity tests, and negative controls where useful.
6. Check measurement: metrics, seeds, variance, uncertainty, failure cases, and qualitative examples.
7. Check reproducibility: code version, data version, configs, hardware, seeds, logs, and artifact paths.
8. State what the experiment can prove, cannot prove, and what would invalidate the conclusion.

## Output Shape

```markdown
# Experiment Design Review

## Claim Under Test
...

## Verdict
- Status: pass / revise / do-not-run-yet
- Biggest risk:

## Issues
| Severity | Issue | Why It Matters | Fix |
|---|---|---|---|

## Baselines And Ablations
- Missing:
- Strong:
- Recommended:

## Measurement Plan
- Metrics:
- Seeds/variance:
- Failure cases:

## Reproducibility Checklist
- ...

## Minimum Fix Before Running
1. ...
```

Use severity labels `blocker`, `major`, `minor`, and `follow-up`.
