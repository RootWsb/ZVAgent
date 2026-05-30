---
name: earnings-filing-reader
description: Earnings and company filing analysis workflow for earnings releases, transcripts, guidance, 10-K, 10-Q, 8-K, S-1, annual reports, shareholder letters, risk factors, segment results, margins, cash flow, debt, buybacks, and disclosure changes. Use when the user asks to summarize a company report, compare a filing with prior periods, identify important financial changes, or extract market-relevant signals from corporate disclosures.
---

# Earnings Filing Reader

## Overview

Use this skill to read company disclosures like an analyst: what changed, why it matters, and which claims need verification.

Prefer Chinese unless the user asks otherwise. Prefer official investor-relations pages and regulatory filings before media summaries.

## Workflow

1. Identify company, ticker, filing or report type, period, reporting date, and source.
2. Extract headline numbers: revenue, growth, gross and operating margin, EPS, free cash flow, debt, cash, buybacks or dividends, and guidance.
3. Compare with prior period and expectations when available.
4. Break down segments, geography, customer mix, demand drivers, margin drivers, orders, or backlog when relevant.
5. Read management commentary and risk factors for changed language.
6. Check earnings quality: one-offs, accounting changes, stock-based compensation, working capital, capex, refinancing, and cash conversion.
7. Identify market-sensitive signals and open questions for the next call or filing.

## Filing Lens

- `10-K` and annual reports: durable business model, risks, segments, accounting policy, long-term trend.
- `10-Q`: quarterly changes, liquidity, working capital, near-term risks.
- `8-K`: event-driven disclosures, earnings releases, guidance, management or legal events.
- `S-1` and prospectuses: ownership, dilution, unit economics, risk factors.
- Earnings transcripts: tone, Q&A pressure points, forward assumptions.

## Output Shape

```markdown
# Filing Read: <company> <period>

## One-Line View
...

## Key Numbers
| Metric | Current | Prior/Expected | Interpretation |
|---|---|---|---|

## What Changed
- Growth:
- Margin:
- Cash flow:
- Balance sheet:
- Guidance:

## Disclosure Signals
...

## Risks And Open Questions
- ...
```

Use `financial-news-impact` after extracting filing facts when the user wants sector or cross-asset implications.
