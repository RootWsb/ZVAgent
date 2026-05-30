---
name: market-report-writer
description: Standardized market research writing workflow for crypto briefs, macro notes, financial news impact reports, token due-diligence memos, earnings readouts, cross-asset analysis, scenario tables, risk framing, and executive summaries. Use when the user asks to turn notes into a professional market report, standardize a crypto or macro brief, write an investment-research style memo, polish financial analysis, or convert messy source notes into a conclusion-evidence-risk-next-steps structure.
---

# Market Report Writer

## Overview

Use this skill to turn market notes into a clean professional memo. It controls structure, risk wording, and scenario framing; it does not make deterministic investment recommendations.

Prefer Chinese unless the user asks otherwise. Pair with `crypto-news`, `economic-analysis`, `financial-news-impact`, `earnings-filing-reader`, or `token-due-diligence` for domain analysis.

## Writing Rules

1. Put the main conclusion first.
2. Separate facts, interpretation, and scenarios.
3. Use explicit timeframes and asset scopes.
4. Compare current data with prior value, expectation, or historical context when available.
5. Include risk and uncertainty, especially for crypto and financial markets.
6. Avoid "must buy/sell" language. Use research framing such as "watch", "risk is rising", "base case", or "requires confirmation".
7. Keep tables compact and decision-useful.
8. Preserve and polish relevant equations from the analysis source. Define variables and state whether a formula is an identity, approximation, model specification, or heuristic.
9. For medium or deep reports, include an **Exhibits** section with 1-3 verified charts, diagrams, or comparison tables when they materially improve interpretation.
10. Every exhibit must include title, timeframe/unit when applicable, source or "conceptual schematic" label, and a one-sentence reading guide.
11. Do not embed an unverified local image path or invent chart data. Verify generated files exist before linking them in Markdown. For conceptual diagrams, prefer fenced Mermaid blocks.
12. Place exhibits in context, not as a loose gallery. Each exhibit should appear immediately after the section or paragraph that uses it as evidence.
13. Match the report surface: dark/transparent backgrounds for generated charts/diagrams, compact layout, restrained accent colors, no decorative white PPT canvases unless quoting a source figure.

## Report Shapes

### Market Brief

```markdown
# Market Brief: <topic/date>

## One-Line View
...

## Key Facts
- ...

## Mechanism
- ...

## Quantitative Framework
$$
<relevant formula, when it improves the analysis>
$$

## Exhibits
![<chart title>](<verified-local-path-or-source-url>)

*Figure 1. <timeframe, source, and what the exhibit shows>.*

## Asset Impact
| Asset/Sector | Direction | Evidence | Confidence |
|---|---|---|---|

## Risks And Uncertainties
- ...

## Watch Points
- ...
```

### Due-Diligence Memo

```markdown
# Research Memo: <asset/company/project>

## Verdict
...

## Evidence
...

## Bull/Bear Cases
...

## Red Flags
...

## Next Checks
...
```

Use `quality-guardrails` before publishing or archiving important reports.
