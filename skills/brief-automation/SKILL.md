---
name: brief-automation
description: Automation workflow for creating, scheduling, drafting, caching, and archiving recurring vertical research briefs across AI technology, cryptocurrency, economics, scientific research, and cross-domain analysis. Use when the user asks for daily or weekly reports, scheduled digests, recurring market/macro/AI updates, automated knowledge-base archiving, brief templates, or a repeatable research pipeline.
---

# Brief Automation

## Overview

Turn one-off analysis workflows into repeatable daily or weekly brief pipelines. Coordinate scheduler tasks, domain skills, source verification, draft generation, and knowledge-base archiving.

Prefer Chinese unless the user asks otherwise.

## Pipeline

Use this workflow for recurring briefs:

1. **Define brief spec**: domain, cadence, time, timezone, audience, depth, output channel, and archive preference.
2. **Select domain skill**:
   - `ai-tech-digest` for AI technology.
   - `crypto-news` for crypto markets.
   - `economic-analysis` for macro and policy.
   - `research-assistant` for papers and research progress.
   - `vertical-research-orchestrator` for cross-domain briefs.
3. **Choose source set**: use `source-registry` to pick official, structured, and specialist sources for the domain.
4. **Fetch or verify sources**: use web/search tools for current facts. Use the crypto script when `CRYPTO_API_KEY` is available.
5. **Generate standardized brief**: follow the vertical response contract unless a domain-specific template is better.
6. **Quality gate**: use `quality-guardrails` before publishing or archiving. Fix fail-level issues.
7. **Archive durable output**: use `knowledge-wiki` and update `knowledge/index.md` and `knowledge/log.md`.
8. **Schedule if requested**: use `scheduler` with `ai_task`, not a fixed message, so the agent can fetch fresh information each run.

## Scheduler Patterns

When the user asks for a recurring digest, create a scheduler task with a precise `ai_task`.
For crypto briefs in a deployment/CLI setup, `crypto-news/scripts/install_crypto_schedule.py` can write the same kind of scheduler task directly into `<workspace>/scheduler/tasks.json`.

Examples:

```text
每天 08:30 AI 技术日报:
Use vertical-research-orchestrator and ai-tech-digest to produce today's AI technology brief. Verify latest model, tooling, open-source, paper, and product updates; use the standard vertical response contract; archive durable items under knowledge/ai-tech/digests/ and update the knowledge index/log.
Before fetching, use source-registry to select primary and specialist AI sources.
Before publishing, use quality-guardrails to validate structure, sources, and archive status.
```

```text
每周一 09:00 加密市场周报:
Use vertical-research-orchestrator, crypto-news, and economic-analysis to produce a weekly crypto market brief. Verify BTC/ETH, major narratives, regulation, liquidity, and macro drivers; include scenarios and risks; archive under knowledge/crypto/briefs/.
Before fetching, use source-registry to select crypto market, regulation, and macro sources.
Before publishing, use quality-guardrails to validate sources and financial risk framing.
```

```text
每天 08:30 加密市场日报:
Use crypto-news to produce today's crypto market brief in Chinese. First run the structured brief generator or fetch current structured data for global market, BTC/ETH, DeFi TVL, stablecoin supply, and stable yield pools. If knowledge/crypto/watchlist.json exists, include its watchlist risk radar. Then verify any breaking news, regulation, ETF, exchange, hack, or macro claims with current sources. Separate facts, inference, and assumptions; include risk framing and avoid deterministic buy/sell instructions. Archive durable output under knowledge/crypto/briefs/ and update knowledge/index.md and knowledge/log.md.
Before publishing, use quality-guardrails to validate sources and financial risk framing.
```

```text
每 2 小时 加密关注列表告警:
Use crypto-news to produce a Chinese crypto watchlist alert. Run generate_crypto_alerts.py with knowledge/crypto/watchlist.json and, if present, knowledge/crypto/social_hot_topics.json. Include market moves, TVL changes, stablecoin liquidity shifts, and social narrative spikes. Treat social discussion as an auxiliary risk signal only; confirm with official project channels, credible news, exchange announcements, liquidation/on-chain data, and current market data. Archive durable alerts under knowledge/crypto/alerts/ and update knowledge/index.md and knowledge/log.md.
Before publishing, use quality-guardrails to validate sources and financial risk framing.
```

CLI installation example:

```bash
python <crypto-news base_dir>/scripts/install_crypto_schedule.py --dry-run
python <crypto-news base_dir>/scripts/install_crypto_schedule.py --workspace <workspace> --channel weixin:wx1 --receiver <receiver_id> --receiver-name "<name>" --cron "30 8 * * *" --replace
```

```text
工作日 08:00 宏观晨报:
Use economic-analysis to produce a macro morning brief. Verify current policy, rates, FX, commodities, and key scheduled data; separate facts, inference, and assumptions; archive durable notes under knowledge/economics/macro-briefs/.
```

Recommended cron values:

| Cadence | Cron | Meaning |
|---|---|---|
| daily morning | `30 8 * * *` | Every day 08:30 |
| workday morning | `0 8 * * 1-5` | Monday-Friday 08:00 |
| weekly Monday | `0 9 * * 1` | Every Monday 09:00 |
| monthly review | `0 9 1 * *` | First day of month 09:00 |

## Draft Script

Use `scripts/create_brief.py` to create a standardized Markdown draft or write it into the knowledge base.
After generating a Markdown draft, validate it with `quality-guardrails/scripts/validate_brief.py` when the file path is available.

```bash
python <base_dir>/scripts/create_brief.py --domain ai-tech --cadence daily --topic "AI 技术日报"
```

To write a draft into a workspace knowledge base:

```bash
python <base_dir>/scripts/create_brief.py --workspace <workspace> --domain ai-tech --cadence daily --topic "AI 技术日报" --write
```

Parameters:

| Parameter | Required | Description |
|---|---|---|
| `--workspace` | no | Agent workspace. Required when `--write` is used. |
| `--domain` | yes | `research`, `crypto`, `economics`, `ai-tech`, or `cross-domain`. |
| `--cadence` | no | `daily`, `weekly`, `monthly`, or `ad-hoc`. |
| `--topic` | no | Human-readable title. |
| `--date` | no | YYYY-MM-DD. Defaults to today. |
| `--sources-json` | no | JSON file with source objects: `title`, `url`, `note`. |
| `--write` | no | Write Markdown and update `knowledge/index.md` and `knowledge/log.md`. |

The script does not fetch the web by itself. It creates a consistent brief shell from already gathered sources, making it safe for scheduler and repeatable workflows.

## Archiving Rules

Use these default folders:

- `knowledge/ai-tech/digests/`
- `knowledge/crypto/briefs/`
- `knowledge/economics/macro-briefs/`
- `knowledge/research/experiments/` or `knowledge/research/literature-maps/`
- `knowledge/cross-domain/`

If the brief contains only transient market noise, send it without archiving. Archive when it includes durable conclusions, source summaries, or reusable analysis.

## Response Style

For setup requests, return:

```markdown
## 自动化方案
- ...

## 调度
- ...

## 数据源
- ...

## 归档位置
- ...

## 下一步
- ...
```

If scheduler is unavailable because `croniter` is missing, tell the user to install `croniter>=2.0.0` and still provide the `ai_task` and cron expression.
