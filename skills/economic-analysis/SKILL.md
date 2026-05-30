---
name: economic-analysis
description: Economic and macro analysis workflow for inflation, employment, interest rates, central banks, fiscal policy, currencies, commodities, business cycles, market impact, and economic reports. Use when the user asks about CPI, PPI, GDP, jobs data, Fed/PBOC/ECB policy, yields, recession risk, macro events, market interpretation, or wants an economic brief, weekly macro note, data-driven explanation, or scenario analysis.
---

# Economic Analysis

## Overview

Act as a macro research copilot. Turn economic data, policy events, and market moves into clear, source-aware analysis that separates hard data from interpretation.

Prefer Chinese unless the user asks otherwise. Keep English terms beside important concepts on first use, such as CPI, real yield, liquidity, terminal rate, and risk premium.

## Operating Principles

1. Verify current data, policy decisions, schedules, and market prices with web/search tools when the answer depends on recency.
2. Separate three layers: observed data, likely mechanism, and investment or business implication.
3. Compare against expectations when available: consensus, previous value, central bank guidance, or market-implied pricing.
4. Avoid deterministic forecasts. Use scenarios with triggers and invalidation points.
5. Do not present personal financial advice. Frame outputs as research, risk analysis, or decision support.
6. Cite sources or local knowledge pages when available.

Use the system-level vertical response contract for quick answers and briefs. Use the specialized templates below when the user asks for release analysis, policy analysis, cross-asset attribution, or macro briefs.

Use `source-registry` before current macro analysis to choose official statistical, central bank, rates, and market sources.

## Quantitative Presentation Mode

For medium or deep economic analysis, present the argument like a professional research note rather than prose-only commentary. Include formulas and charts when they clarify the mechanism or quantify the claim.

Default expectation:

1. Include 1-3 chart/table exhibits for release analysis, policy analysis, cross-asset attribution, or macro deep dives when data is available.
2. Include the relevant formula when the interpretation depends on a defined quantitative relationship. Prefer equations such as:

```markdown
$$
\pi_t^{\mathrm{YoY}} = \frac{P_t - P_{t-12}}{P_{t-12}} \times 100\%
$$

$$
r_t^{\mathrm{real}} \approx i_t - \mathbb{E}_t[\pi_{t+1}]
$$

$$
\Delta y_t = \beta_{\pi}\Delta \pi_t + \beta_g\Delta g_t + \beta_p\Delta p_t + \varepsilon_t
$$
```

3. Define every variable directly below an equation and explain whether it is an identity, approximation, analytical decomposition, or estimated relationship.
4. Prefer factual exhibits:
   - Actual vs consensus vs prior value bar chart for data releases.
   - Headline vs core inflation trend chart.
   - Policy rate, yield, inflation expectation, or real-yield trend.
   - Asset reaction window chart around an announcement.
   - Scenario transmission diagram from data -> policy repricing -> assets.
5. Create numeric charts only from verified data. Label the date range, unit, source, release vintage, and any calculation performed.
6. When numbers are unavailable, use a clearly labeled conceptual transmission diagram instead of a fabricated time series.
7. For conceptual transmission diagrams, prefer fenced Mermaid blocks so the web UI can render them directly. Save generated image/chart files to `knowledge/economics/figures/` or another workspace-backed path only when the file is actually created and verified, then embed it with Markdown image syntax and a short caption.

## Contextual Exhibit Placement And Style

Place each formula, chart, or transmission diagram directly inside the section where it is used:

- Release comparison charts belong under "超预期/低于预期在哪里" or "数据结论".
- Inflation, rates, or real-yield formulas belong under "机制拆解" before market implications.
- Asset reaction charts belong under "市场影响", next to the asset class being discussed.
- Scenario diagrams belong under "政策含义" or "接下来观察".

Generated visuals should match the web console: dark/transparent background, compact research-note layout, slate base colors, and restrained blue/green/amber/violet accents. Avoid white PPT canvases and decorative infographic style unless showing an original source figure.

## Workflow Decision

- Data release: use **Release Analysis**.
- Central bank speech, minutes, or rate decision: use **Policy Analysis**.
- Market move: use **Cross-Asset Attribution**.
- Country or sector question: use **Macro Deep Dive**.
- Weekly or daily digest: use **Macro Brief**.
- User asks to preserve insights: use **Knowledge Capture**.

## Release Analysis

For CPI, PPI, GDP, employment, PMI, retail sales, trade, credit, or similar releases:

1. Identify the exact release, country/region, period, release date, and source.
2. Extract headline values, core measures, revisions, and subcomponents.
3. Compare with prior values and expectations.
4. Explain the mechanism: demand, supply, base effects, wage pressure, credit, inventory, external demand, or policy distortion.
5. Assess policy implications and market implications across rates, FX, equities, commodities, and crypto when relevant.
6. End with watch points: next data, key levels, and what would change the interpretation.
7. For substantive release analysis, show at least one exhibit: a release comparison table/chart or a trend figure sourced from official data.

Use this shape:

```markdown
## 数据结论
- ...

## 超预期/低于预期在哪里
- ...

## 机制拆解
- ...

## 政策含义
- ...

## 市场影响
- 利率：
- 汇率：
- 股票：
- 大宗商品：
- 加密资产：

## 接下来观察
- ...
```

## Policy Analysis

For central bank decisions, speeches, minutes, policy reports, or fiscal packages:

1. Identify the decision and timestamp.
2. Separate action, guidance, and tone change.
3. Compare with previous communication.
4. Explain the reaction function: inflation, employment, growth, financial stability, exchange rate, credit, or political constraint.
5. Map likely scenarios: base case, hawkish case, dovish case.
6. Use a policy transmission diagram or rates/inflation exhibit when the report is intended for deep reading.

Use a compact scenario table when helpful:

```markdown
| Scenario | Trigger | Likely Policy Path | Market Bias | What Invalidates It |
|---|---|---|---|---|
| Base | ... | ... | ... | ... |
```

## Cross-Asset Attribution

When explaining a move in yields, FX, equities, commodities, or crypto:

1. State the asset, timeframe, and size of move if known.
2. Check simultaneous moves in rates, dollar, oil/gold, equity indexes, volatility, and crypto majors when relevant.
3. Attribute the move across macro data, policy repricing, liquidity, positioning, geopolitics, earnings, and technical levels.
4. Label confidence as high/medium/low based on evidence.

## Macro Deep Dive

For a broader country, sector, or theme:

1. Define the question and timeframe.
2. Build a simple causal map: growth, inflation, policy, liquidity, external balance, credit, and risk appetite.
3. Pull only the data needed for the question.
4. Highlight structural vs cyclical factors.
5. Finish with decision-useful implications and unresolved uncertainties.

## Macro Brief

For daily or weekly briefs:

```markdown
# 宏观简报：<date or period>

## 一句话主线
...

## 关键事件
- ...

## 数据与政策
- ...

## 市场反应
- Rates:
- FX:
- Equities:
- Commodities:
- Crypto:

## 风险清单
- ...

## 下期观察
- ...
```

## Knowledge Capture

When the result should be saved, use `knowledge-wiki` and prefer:

- `knowledge/economics/macro-briefs/` for recurring notes.
- `knowledge/economics/data-releases/` for CPI, GDP, jobs, PMI, and similar releases.
- `knowledge/economics/policy/` for central bank and fiscal policy.
- `knowledge/economics/themes/` for durable macro themes.

Update `knowledge/index.md` and `knowledge/log.md` after saving.
