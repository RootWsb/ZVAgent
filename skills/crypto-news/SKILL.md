---
name: crypto-news
description: Cryptocurrency market intelligence workflow for Bitcoin, Ethereum, altcoins, DeFi, stablecoins, ETFs, on-chain narratives, regulation, token events, and market risk. Use when the user asks about crypto news, coin analysis, market trends, price moves, DeFi, blockchain projects, tokenomics, exchange or regulatory events, or wants a crypto daily/weekly brief.
---

# Crypto News & Analysis

## Overview

Act as a crypto research copilot. Combine market data, news, narratives, macro context, and risk framing into concise analysis.

Prefer Chinese unless the user asks otherwise. Do not provide deterministic buy/sell instructions. Frame outputs as research, risk analysis, and scenario planning.

Use the system-level vertical response contract for quick answers and briefs. Use the specialized templates below when the user asks for market briefs, asset deep dives, event analysis, or risk review.

Use `source-registry` before current market or news analysis to choose market-data, official, regulatory, and specialist crypto sources.

## Quantitative And Visual Presentation

For medium or deep crypto analysis, combine narrative, verifiable market/on-chain metrics, formulas, and exhibits. A professional crypto note should make the evidence inspectable, not merely add decorative images.

Default expectation:

1. Include 1-3 exhibits when structured data is available:
   - BTC/ETH price or drawdown comparison over the stated horizon.
   - Volume, market cap, BTC dominance, stablecoin supply, or DeFi TVL trend.
   - Protocol TVL or yield comparison.
   - Event timeline and before/after market reaction.
   - Risk radar table for liquidity, unlock, concentration, counterparty, or security exposure.
2. Use equations when explaining computed metrics. Useful forms include:

```markdown
$$
R_{t,h} = \frac{P_t - P_{t-h}}{P_{t-h}} \times 100\%
$$

$$
\mathrm{Drawdown}_t = \frac{P_t - \max_{s \leq t}P_s}{\max_{s \leq t}P_s} \times 100\%
$$

$$
\mathrm{Turnover}_t = \frac{\mathrm{Volume}_{24h,t}}{\mathrm{MarketCap}_t}
$$

$$
\mathrm{TVLChange}_{h} = \frac{\mathrm{TVL}_t - \mathrm{TVL}_{t-h}}{\mathrm{TVL}_{t-h}} \times 100\%
$$
```

3. Define variables, timeframe, currency/unit, data source, and query timestamp underneath each calculated metric or chart.
4. Do not turn a price chart into a causal claim. Separate the plotted observation from hypotheses about catalysts, positioning, macro liquidity, or narratives.
5. Generate numeric charts only from retrieved structured data. For mechanisms such as liquidation cascades, stablecoin depeg propagation, or bridge exploit impact, conceptual flow diagrams are acceptable when labeled as conceptual.
6. For conceptual flow diagrams, prefer fenced Mermaid blocks so the web UI can render them directly. Save created chart/diagram files under `knowledge/crypto/figures/` or another workspace-backed path only when the file actually exists, then embed them with Markdown plus a concise caption.
7. For very short updates, a compact metrics table is enough; do not generate a picture for decoration alone.

## Contextual Exhibit Placement And Style

Place crypto visuals next to the exact claim they support:

- Price/return/drawdown charts belong next to the price-action discussion.
- TVL, stablecoin, or yield charts belong next to liquidity or protocol-fundamental analysis.
- Unlock, exploit, ETF, lawsuit, or listing timelines belong next to event analysis.
- Risk radar tables belong next to portfolio/watchlist risk review.

Generated visuals should look like research-console exhibits: dark or transparent background, compact spacing, thin borders, readable labels, and a restrained palette. Avoid bright white infographic canvases, hype poster styling, and decorative token imagery unless the user explicitly asks for presentation graphics.

## Data Sources

Prefer the bundled script for structured market, DeFi, stablecoin, and yield data. CoinGecko public endpoints and DefiLlama endpoints work without a key; if `CRYPTO_API_KEY` or `COINGECKO_API_KEY` is configured, the script will pass it to CoinGecko.

```bash
python <base_dir>/scripts/fetch_crypto_data.py '{"action": "market_overview", "count": 20}'
python <base_dir>/scripts/fetch_crypto_data.py '{"action": "global_market"}'
python <base_dir>/scripts/fetch_crypto_data.py '{"action": "coin_detail", "coin_id": "bitcoin"}'
python <base_dir>/scripts/fetch_crypto_data.py '{"action": "trend_analysis", "coin_id": "ethereum"}'
python <base_dir>/scripts/fetch_crypto_data.py '{"action": "defi_overview", "count": 20}'
python <base_dir>/scripts/fetch_crypto_data.py '{"action": "defi_overview", "include_cex": true, "count": 20}'
python <base_dir>/scripts/fetch_crypto_data.py '{"action": "stablecoin_overview", "count": 20}'
python <base_dir>/scripts/fetch_crypto_data.py '{"action": "yield_pools", "stable_only": true, "min_tvl_usd": 10000000}'
python <base_dir>/scripts/fetch_crypto_data.py '{"action": "protocol_detail", "slug": "lido"}'
```

For a ready-to-send market brief, use the bundled brief generator:

```bash
python <base_dir>/scripts/generate_crypto_brief.py --cadence daily --topic "加密市场日报" --stable-yields
python <base_dir>/scripts/generate_crypto_brief.py --workspace <workspace> --write --cadence daily --topic "加密市场日报" --stable-yields --json
python <base_dir>/scripts/generate_crypto_brief.py --watchlist <workspace>/knowledge/crypto/watchlist.json --cadence daily --topic "加密市场日报" --stable-yields
```

For watchlist alerts that include optional social narrative spikes:

```bash
python <base_dir>/scripts/generate_crypto_alerts.py --workspace <workspace> --include-liquidity
python <base_dir>/scripts/generate_crypto_alerts.py --workspace <workspace> --social-json <workspace>/knowledge/crypto/social_hot_topics.json --write --json
python <base_dir>/scripts/generate_crypto_alerts.py --watchlist <workspace>/knowledge/crypto/watchlist.json --social-json <workspace>/knowledge/crypto/social_hot_topics.json
```

To install a recurring scheduler task directly into a deployed workspace:

```bash
python <base_dir>/scripts/install_crypto_schedule.py --dry-run
python <base_dir>/scripts/install_crypto_schedule.py --workspace <workspace> --channel weixin:wx1 --receiver <receiver_id> --receiver-name "<name>" --cron "30 8 * * *" --replace
```

If the script fails, use web/search tools and cite sources. For breaking news or prices, verify recency before analysis.

Supported script actions:

| action | purpose |
|---|---|
| `market_overview` | Top coins, market cap, 24h change, volume |
| `global_market` | Total crypto market cap, volume, BTC/ETH dominance, DeFi aggregate |
| `news` | Crypto news aggregation |
| `coin_detail` | Deep dive into one coin |
| `trend_analysis` | Market trend and pattern summary |
| `defi_overview` | Top DeFi protocols, chains, and TVL categories; excludes CEX reserves unless `include_cex` is true |
| `protocol_detail` | DefiLlama protocol detail and recent TVL history |
| `stablecoin_overview` | Stablecoin supply by asset and chain |
| `yield_pools` | DeFi yield pools filtered by chain/project/stablecoin/min TVL |

## Automated Brief Generator

Use `generate_crypto_brief.py` when the user asks for a daily, weekly, or recurring crypto market brief and a structured draft is enough.

Arguments:

| argument | purpose |
|---|---|
| `--cadence daily|weekly|monthly|ad-hoc` | Brief cadence label |
| `--topic` | Human-readable title |
| `--stable-yields` | Restrict yield section to stablecoin pools |
| `--min-yield-tvl` | Minimum yield pool TVL in USD |
| `--watchlist` | Add watchlist risk radar from a JSON file |
| `--write --workspace <workspace>` | Archive to `knowledge/crypto/briefs/` and update `knowledge/index.md` / `knowledge/log.md` |
| `--json` | Print machine-readable write result |

The generator uses structured data only. Before publishing a high-stakes or breaking-news brief, supplement it with fresh news/regulatory checks and run quality review.

## Watchlist Alert Generator

Use `generate_crypto_alerts.py` when the user wants event-style alerts for a watchlist, especially when market moves may be driven by social attention.

Arguments:

| argument | purpose |
|---|---|
| `--workspace` | ZVAgent workspace. Defaults watchlist/social paths under `knowledge/crypto/` |
| `--watchlist` | Explicit watchlist JSON path |
| `--social-json` | Optional social hot topics JSON path |
| `--include-liquidity` | Also check major-chain stablecoin supply moves |
| `--write --workspace <workspace>` | Archive to `knowledge/crypto/alerts/` and update `knowledge/index.md` / `knowledge/log.md` |
| `--json` | Print machine-readable result |

Social input contract:

```json
{
  "timestamp": "2026-05-22T09:00:00+08:00",
  "sources": [{"name": "X/Twitter", "url": "https://x.com/search?q=BTC"}],
  "topics": [
    {
      "asset": "BTC",
      "coin_id": "bitcoin",
      "protocol_slug": "",
      "topic": "ETF flow discussion",
      "mentions": 1200,
      "sentiment": "positive",
      "sentiment_score": 0.68,
      "velocity_24h_pct": 240,
      "sample_links": ["https://example.com/post"],
      "notes": "Short context for the discussion spike."
    }
  ]
}
```

Use social platforms as a narrative and risk layer, not as a standalone decision engine. A useful rule:

- Social spike + price/TVL confirmation: event deserves follow-up.
- Social spike without market/on-chain confirmation: watch-only narrative risk.
- Negative social spike + price/TVL weakness: stress-confirmation signal requiring official/news verification.
- Extreme positivity, meme-like velocity, or one-sided promotion: manipulation and crowded-trade risk.

## Watchlist Risk Radar

Use `manage_crypto_watchlist.py` when the user wants persistent monitoring of specific coins or protocols.

```bash
python <base_dir>/scripts/manage_crypto_watchlist.py --workspace <workspace> init
python <base_dir>/scripts/manage_crypto_watchlist.py --workspace <workspace> add-coin --id bitcoin --symbol BTC --name Bitcoin --tags core,macro
python <base_dir>/scripts/manage_crypto_watchlist.py --workspace <workspace> add-protocol --slug lido --name Lido --tags liquid-staking,eth
python <base_dir>/scripts/manage_crypto_watchlist.py --workspace <workspace> list
python <base_dir>/scripts/manage_crypto_watchlist.py --workspace <workspace> remove bitcoin
```

Default file: `knowledge/crypto/watchlist.json`.

Supported asset types:

| type | required field | data source |
|---|---|---|
| `coin` | `id` | CoinGecko coin id |
| `protocol` | `slug` | DefiLlama protocol slug |

Risk radar checks:

- Coin 24h/7d moves, volume-to-market-cap turnover, and deep ATH drawdown.
- Protocol recent TVL move, chain concentration, and low TVL.
- Thresholds live in `watchlist.settings` and can be edited directly when needed.
- Alert thresholds can also include `social_mentions_alert_min`, `social_velocity_alert_pct`, `social_sentiment_abs_alert`, `ath_drawdown_alert_pct`, and `stablecoin_1d_alert_pct`.

## Workflow Decision

- General market question: use **Market Brief**.
- Specific coin or protocol: use **Asset Deep Dive**.
- Breaking event: use **Event Analysis**.
- Portfolio/watchlist question: use **Risk Review**.
- User wants saved output: use **Knowledge Capture**.

## Market Brief

1. Check BTC, ETH, total crypto market direction, stablecoin/liquidity clues, major altcoin dispersion, and macro risk appetite.
2. Identify top narratives: ETF flows, regulation, L2, restaking, DeFi, stablecoins, AI tokens, memecoins, infrastructure, or security incidents.
3. Separate price action from causal interpretation.
4. State risk regime: risk-on, risk-off, rotation, liquidity squeeze, or event-driven.
5. Use `global_market`, `market_overview`, `stablecoin_overview`, and `defi_overview` when a current structured brief is needed.
6. For a deep brief, include at least one current market exhibit and identify its data timestamp.

Use this shape:

```markdown
# Crypto 简报：<date or period>

## 一句话市场状态
...

## 关键数据
- BTC:
- ETH:
- 市场广度/成交量:

## 新闻与叙事
- ...

## 风险因素
- ...

## 24-72 小时观察
- ...
```

## Asset Deep Dive

For a coin, token, chain, or protocol:

1. Identify ticker, project, sector, chain, and source links.
2. Cover price/volume, catalyst, tokenomics, unlocks/emissions, ecosystem activity, competitors, and security/regulatory risks.
3. Explain whether movement is driven by fundamentals, narrative, liquidity, listings, leverage, or one-off events.
4. End with scenarios and invalidation points.
5. For coins, use `coin_detail` and `trend_analysis`. For DeFi protocols, use `protocol_detail`, `defi_overview`, and `yield_pools` where relevant.
6. Show computed return/drawdown, TVL change, or valuation/liquidity comparison when underlying data supports it.

## Event Analysis

For hacks, ETF decisions, lawsuits, exchange listings, protocol upgrades, airdrops, unlocks, or governance votes:

1. Verify the event from primary or high-quality sources.
2. Explain what happened, affected assets, timeline, and direct impact.
3. Separate immediate market reaction from medium-term implications.
4. List unresolved facts and what to monitor next.

## Risk Review

For user watchlists or portfolio-like questions:

1. Ask for missing holdings/time horizon only if necessary.
2. Analyze concentration, correlation, liquidity, event risk, unlocks, leverage sensitivity, regulatory exposure, and stablecoin/counterparty exposure.
3. Provide risk controls as neutral research options, not instructions.
4. Use `stablecoin_overview` for liquidity and peg-risk context, `defi_overview` for ecosystem risk, and `yield_pools` only as research input rather than a yield recommendation.
5. If a watchlist exists, use `generate_crypto_brief.py --watchlist ...` or inspect `knowledge/crypto/watchlist.json` for persistent monitoring context.
6. If social narratives are part of the question, use `generate_crypto_alerts.py --social-json ...` and treat social activity as cross-checkable risk context.

## Knowledge Capture

When saving crypto research, use `knowledge-wiki` and prefer:

- `knowledge/crypto/briefs/` for daily or weekly market briefs.
- `knowledge/crypto/assets/` for coin and protocol notes.
- `knowledge/crypto/events/` for hacks, regulatory events, ETFs, listings, and unlocks.
- `knowledge/crypto/themes/` for durable narratives.

Update `knowledge/index.md` and `knowledge/log.md` after saving.

## Scheduler Pattern

For recurring briefs, use `brief-automation` and create a scheduler task with `ai_task` instead of a fixed message. A good daily task description:

```text
Use crypto-news to produce today's crypto market brief in Chinese. First run the structured brief generator or fetch current structured data for global market, BTC/ETH, DeFi TVL, stablecoin supply, and stable yield pools. If knowledge/crypto/watchlist.json exists, include its watchlist risk radar. Then verify any breaking news, regulation, ETF, exchange, hack, or macro claims with current sources. Separate facts, inference, and assumptions; include risk framing and avoid deterministic buy/sell instructions. Archive durable output under knowledge/crypto/briefs/ and update knowledge/index.md and knowledge/log.md.
```

A good intraday alert task description:

```text
Use crypto-news to produce a Chinese crypto watchlist alert. Run generate_crypto_alerts.py with knowledge/crypto/watchlist.json and, if present, knowledge/crypto/social_hot_topics.json. Treat social hot topics as narrative/risk signals only: confirm with price, TVL, stablecoin liquidity, official project channels, exchange announcements, credible news, and on-chain data. Do not produce deterministic buy/sell instructions. Archive durable alerts under knowledge/crypto/alerts/ and update knowledge/index.md and knowledge/log.md.
```

If configuring from the command line, use `install_crypto_schedule.py`. It writes `<workspace>/scheduler/tasks.json`, supports `--dry-run`, and requires `--receiver` unless dry-running. Use `--replace` when updating the same scheduled brief.
