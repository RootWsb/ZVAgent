---
name: quality-guardrails
description: Quality validation and failure-protection workflow for vertical research briefs, AI digests, crypto market notes, macro analysis, scientific research notes, scheduled reports, and knowledge-base archiving. Use when checking whether an answer has required sections, sources, current-information verification, risk disclosure, financial/crypto safety framing, knowledge index/log updates, or when a scheduled automation/data source fails and needs graceful degradation.
---

# Quality Guardrails

## Overview

Use this skill as the final inspection layer for vertical research output. It catches missing evidence, weak structure, unsafe financial framing, stale-data risk, and incomplete knowledge-base archiving.

Prefer Chinese for user-facing summaries unless the user asks otherwise.

## When To Run

Run this skill before publishing or archiving:

- Daily/weekly/monthly briefs from `brief-automation`.
- Current AI model/API/repo updates.
- Crypto and macro market analysis.
- Research notes meant for `knowledge/`.
- Any answer that makes source-sensitive claims.

For simple conversational answers, do not overuse this skill.

## Validation Checklist

Check these items:

1. **Structure**: includes `结论`, `依据`, `风险/不确定性`, and `下一步`, or a domain-specific equivalent.
2. **Evidence**: includes source links, local paths, or clear "pending verification" markers.
3. **Current-data discipline**: latest/prices/policy/API/regulation claims mention verification or current sources.
4. **Fact vs inference**: important judgments separate facts, inference, and assumptions.
5. **Financial/crypto safety**: no deterministic buy/sell instruction; includes risk framing.
6. **Knowledge archiving**: if saved to `knowledge/`, confirms `knowledge/index.md` and `knowledge/log.md` updates.
7. **Failure handling**: if a data source or scheduler failed, states fallback sources and uncertainty.

## Script

Use `scripts/validate_brief.py` for quick Markdown validation:

```bash
python <base_dir>/scripts/validate_brief.py <brief.md>
python <base_dir>/scripts/validate_brief.py <brief.md> --domain crypto --require-sources
python <base_dir>/scripts/validate_brief.py <brief.md> --json
```

Parameters:

| Parameter | Description |
|---|---|
| `path` | Markdown file to validate. |
| `--domain` | Optional: `ai-tech`, `crypto`, `economics`, `research`, `cross-domain`. |
| `--require-sources` | Fail if no URL, source block, or local citation appears. |
| `--require-archive` | Warn if no knowledge/index/log mention appears. |
| `--json` | Output machine-readable result. |

## Scoring

Use this interpretation:

- `pass`: publishable with normal review.
- `warn`: usable, but mention gaps or fix before scheduled automation.
- `fail`: fix before publishing or archiving.

## Failure Protection

When data sources fail:

1. Do not invent fresh facts.
2. State the failure plainly.
3. Use the next best source family from `source-registry`.
4. Mark the result as partial.
5. Preserve the failed source and timestamp in the brief if useful.

When scheduler fails or is unavailable:

1. Check whether `croniter>=2.0.0` is installed.
2. Provide the intended cron expression and `ai_task` anyway.
3. Tell the user the automation is not active until scheduler is available.

## Response Shape

For validation results, use:

```markdown
## 质量结论
- Status:
- Score:

## 问题
- ...

## 建议修复
- ...

## 是否可以发布
...
```
