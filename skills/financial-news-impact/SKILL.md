---
name: financial-news-impact
description: Financial news impact analysis workflow for market-moving company, sector, macro, policy, credit, rates, FX, commodities, earnings, M&A, sanctions, geopolitics, and liquidity news. Use when the user asks why markets moved, how a financial news item may affect assets, sectors, risk appetite, crypto, or macro expectations, or wants a concise scenario-based market impact note.
---

# Financial News Impact

## Overview

Use this skill to convert a news item into market implications without pretending certainty. It bridges macro analysis and company or sector news.

Prefer Chinese unless the user asks otherwise. Verify news, prices, rates, policy, and market reaction when the answer depends on recency.

## Workflow

1. Identify the news: source, timestamp, affected entity, geography, sector, and confirmation status.
2. Separate the hard fact from the market narrative.
3. Check immediate reaction when relevant: equities, rates, FX, commodities, credit, volatility, and crypto majors.
4. Map transmission channels: earnings, discount rates, liquidity, policy expectations, supply chain, demand, balance sheet, positioning, and sentiment.
5. Classify the event as idiosyncratic, sector-wide, macro, or systemic.
6. Build base, upside, and downside scenarios with invalidation points.
7. State confidence and missing evidence.

## Output Shape

```markdown
# Financial News Impact: <event>

## One-Line View
...

## Facts vs Narrative
- Fact:
- Narrative:
- Confidence:

## Transmission Channels
| Channel | Direction | Evidence | Uncertainty |
|---|---|---|---|

## Asset And Sector Impact
- Rates:
- FX:
- Equities:
- Commodities:
- Credit:
- Crypto:

## Scenarios
| Scenario | Trigger | Implication | Invalidation |
|---|---|---|---|

## Watch Points
- ...
```

Do not present personal financial advice as certainty.
