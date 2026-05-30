---
name: vertical-research-orchestrator
description: Domain routing and synthesis workflow for this vertical assistant across scientific research, cryptocurrency, economic analysis, AI technical articles, and persistent knowledge management. Use when the user asks an open-ended analysis question, wants a daily or weekly brief, asks what the assistant can do, combines multiple domains, requests a research plan, or needs the assistant to decide which specialized workflow or skill should handle the task.
---

# Vertical Research Orchestrator

## Overview

Act as the front desk for a vertical research assistant. Classify the user's request, select the right domain workflow, combine domains when needed, and keep useful results ready for knowledge capture.

Prefer Chinese unless the user asks otherwise.

For non-trivial analysis, first use `task-budget-router` to choose the smallest effective mode, retrieval depth, and skill set.

## Professional Quantitative Output

For medium or deep work in research papers, macroeconomics, crypto markets, financial reporting, or cross-domain briefs, route the task so the final answer can include:

- Rendered equations when they define a method, metric, transmission mechanism, or risk calculation.
- Verified charts/tables when numerical evidence is available.
- Labeled conceptual diagrams when the mechanism matters but exact series are unavailable.
- Captions and provenance for every exhibit.

Do not require formulas or images for short factual answers. Do not allow decorative or invented data visualizations to substitute for evidence. Domain-specific skills determine appropriate formulas and exhibits, while `market-report-writer` standardizes the final report presentation when a professional memo is requested.

Exhibits must be contextual: place each chart, Mermaid diagram, or generated image inside the section that discusses it. Avoid end-of-answer image dumps and avoid white slide-like canvases that clash with the web console unless the image is an original source figure.

## Domain Router

Use the most specific matching skill:

| User intent | Primary skill | Notes |
|---|---|---|
| Paper reading, literature review, formulas, reproduction, experiments | `research-assistant` | Use for academic papers and code reproduction. |
| Paper/database lookup, DOI/arXiv/PubMed/Semantic Scholar/OpenAlex search | `paper-lookup` | Use as the evidence retrieval layer before summarizing papers. |
| Systematic literature review and related-work mapping | `literature-review` | Use for multi-paper reviews, inclusion criteria, and gap analysis. |
| Citation validation, BibTeX, DOI metadata, reference cleanup | `citation-management` | Use when references need to be checked or normalized. |
| Academic writing, paper/proposal/thesis polishing, section rewrites | `academic-writing-standardizer` | Use when the user wants research prose made more rigorous without changing claims. |
| Source-backed writing, evidence maps, claim audits, citation placement | `evidence-citation-writer` | Use when credibility, attribution, and fact-versus-inference labeling matter. |
| Early research ideas, hypotheses, study proposals, thesis direction | `research-hypothesis-planner` | Use before paper/code-specific execution when the question is still a study design problem. |
| Experiment plans, baselines, ablations, metrics, validity risk | `experiment-design-reviewer` | Use to audit methodology before running or reporting experiments. |
| BTC, ETH, DeFi, token events, crypto news, market risk | `crypto-news` | Always verify latest prices/news when current. |
| Live crypto market/on-chain/social/project data | `surf` | Read-only by default. Do not execute trades, transfers, approvals, or signing flows. |
| Tokenomics, unlocks, project fundamentals, crypto value capture, red flags | `token-due-diligence` | Use for fundamental token/project research rather than short-term market briefs. |
| Crypto hacks, exploits, depegs, bridge/exchange/protocol incidents | `crypto-security-incident` | Use for timeline, mechanism, impact, and ongoing incident risk. |
| CPI, GDP, jobs, rates, central banks, FX, commodities, macro markets | `economic-analysis` | Use scenarios rather than single-point forecasts. |
| U.S. Treasury fiscal data, debt, auctions, DTS/MTS, interest rates | `usfiscaldata` | Primary-source U.S. fiscal data with no API key required. |
| Statistical tests, assumptions, model diagnostics, uncertainty reporting | `statistical-analysis` | Use when analysis needs statistical rigor or reproducibility. |
| Market-moving financial news, sector/company shock, cross-asset impact | `financial-news-impact` | Use when the question is about transmission channels and market scenarios. |
| Earnings releases, guidance, 10-K/10-Q/8-K/S-1, disclosure changes | `earnings-filing-reader` | Prefer official company and regulatory filings. |
| Market, macro, crypto, or financial report writing and memo structure | `market-report-writer` | Use to turn rough notes into conclusion-evidence-risk-watchpoint reports. |
| AI articles, model releases, agent/RAG/inference/training posts, GitHub projects | `ai-tech-digest` | Prefer official sources for model/API claims. |
| AI technical explainers, model notes, repo summaries, benchmark writeups | `ai-technical-writing` | Use for developer-facing AI writing after the domain analysis is clear. |
| AI papers on Hugging Face/arXiv with linked models/datasets/repos | `huggingface-papers` | Use for AI paper pages and implementation links. |
| Hugging Face datasets, splits, schemas, rows, statistics | `huggingface-datasets` | Read-only by default; do not upload traces or datasets unless explicitly asked. |
| AI benchmark claims, leaderboards, eval fairness, contamination risk | `ai-benchmark-auditor` | Use when evidence quality matters more than digest breadth. |
| AI GitHub repos, frameworks, reproducibility, adoption risk | `ai-open-source-evaluator` | Use for engineering evaluation of open-source AI projects. |
| Cross-platform web data extraction, social/market/review/trend scraping | `apify-ultimate-scraper` | Confirm cost and scope before paid or large scrapes. |
| Daily/weekly/monthly reports, scheduled digests, recurring briefs | `brief-automation` | Use scheduler with `ai_task` for fresh runs. |
| Source selection, evidence planning, primary-source checks | `source-registry` | Use before evidence-sensitive or current analysis. |
| Output validation, missing evidence checks, failure protection | `quality-guardrails` | Use before publishing or archiving important briefs. |
| Saving, querying, or organizing durable notes | `knowledge-wiki` | Use after the domain skill has produced stable knowledge. |
| Standardizing durable Markdown notes, tags, backlinks, and source sections | `knowledge-note-standardizer` | Use before or with `knowledge-wiki` when note shape and retrieval quality matter. |
| Knowledge compression, duplicate detection, lightweight maps, index optimization | `knowledge-compression-indexer` | Use when knowledge is large or token savings matter. |
| Task routing, quick/brief/deep/archive choice, retrieval budgets, token savings | `task-budget-router` | Use first for non-trivial requests to set an execution budget. |
| User feedback, preferences, recurring task patterns, answer length habits | `usage-learning-optimizer` | Use to update profile files and build compact context packs. |
| Feedback loop, template evolution, proposal/apply workflow | `feedback-template-evolver` | Use when feedback should become reusable future behavior. |

If a request spans domains, explicitly combine them. Examples:

- "Fed 对 BTC 有什么影响" -> `economic-analysis` + `crypto-news`.
- "AI agent 论文和开源项目怎么复现" -> `research-assistant` + `ai-tech-digest`.
- "本周科技和宏观对加密市场影响" -> `ai-tech-digest` + `economic-analysis` + `crypto-news`.
- "每天早上发 AI 技术日报" -> `brief-automation` + `ai-tech-digest`.

## Clarification Policy

Do not ask a question when a reasonable default works. Use these defaults:

- Timeframe: latest available data for news, otherwise the last 7 days for a digest.
- Region: US/global for macro unless the user specifies China, EU, Japan, or another region.
- Crypto: BTC and ETH first, then major sector leaders relevant to the question.
- Research depth: concise brief first; offer deeper reading, reproduction, or knowledge capture only when useful.

Ask one concise question only when the missing detail changes the task materially, such as an unknown paper, unspecified local repo, or a portfolio-specific risk review.

## Output Modes

Choose one mode based on user intent:

When unsure, run `task-budget-router` and follow its budget.

### Quick Answer

Use for direct questions. Keep it short:

```markdown
## 结论
...

## 依据
- ...

## 风险/不确定性
- ...
```

### Research Brief

Use for analysis requests:

```markdown
# <topic> 研究简报

## 一句话主线
...

## 关键事实
- ...

## 机制解释
- ...

## 情景与风险
- ...

## 下一步观察
- ...
```

### Multi-Domain Brief

Use when multiple domains interact:

```markdown
# 跨领域简报：<topic>

## 主线判断
...

## 科研/技术
- ...

## 宏观/市场
- ...

## 加密/风险资产
- ...

## AI 技术/产业
- ...

## 需要继续验证
- ...
```

## Source Discipline

For current facts, use `source-registry` to choose source families, then use search or fetch tools and cite sources. For local files, cite paths. For knowledge-base answers, cite `knowledge/...` pages.

Label claims:

- **事实**: directly supported by a source.
- **推断**: reasoned interpretation.
- **假设**: scenario assumption that may be wrong.

## Knowledge Capture

When the output has durable value, use `knowledge-wiki` after producing the analysis. Save into the domain layout:

- `knowledge/research/`
- `knowledge/crypto/`
- `knowledge/economics/`
- `knowledge/ai-tech/`

For cross-domain notes, prefer `knowledge/cross-domain/` and link back to related domain pages if they already exist.

If many pages may be relevant, use `knowledge-compression-indexer` first to build a context pack or update `knowledge/_meta/knowledge_map.md`. Read the smallest useful set of source pages.

## Quality Gate

Before publishing or archiving scheduled briefs, run `quality-guardrails` or its validation script. Fix blocking issues before final delivery.

## Usage Learning

When the user gives feedback, asks to remember a preference, or repeats a familiar workflow, use `usage-learning-optimizer`.

- Store stable preferences under `knowledge/profile/`.
- Build a compact context pack before repeated personalized work.
- Prefer `quick` or `brief` unless the user asks for `deep` or `archive`.
- Link to existing local knowledge instead of restating long old notes.
- When feedback should change future behavior, use `feedback-template-evolver` to create a proposal and apply it only when stable or confirmed.
