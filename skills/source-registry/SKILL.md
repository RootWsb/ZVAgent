---
name: source-registry
description: Trusted source selection workflow and machine-readable source catalog for vertical research in AI technology, cryptocurrency, economics, and scientific research. Use when the assistant needs to choose data sources, verify current facts, prepare a daily or weekly brief, cite primary sources, design a source pipeline, or explain which sources should be used for a domain-specific analysis.
---

# Source Registry

## Overview

Use this skill to choose reliable data sources before doing current or evidence-sensitive research. It keeps source selection explicit, repeatable, and aligned across the vertical assistant.

Prefer primary and official sources for facts, then use secondary sources for interpretation, discovery, and market color.

## Source Priority

1. **Primary/official**: project docs, company blogs, central banks, government data, exchanges, chain/project announcements, paper pages.
2. **Structured data providers**: APIs, datasets, official calendars, GitHub metadata, arXiv/Semantic Scholar records.
3. **Reputable specialist media**: domain-specific reporting and analysis.
4. **Aggregators/social signals**: useful for discovery, never enough alone for factual claims.

For breaking or market-moving claims, confirm with at least one primary or high-quality source before presenting it as fact.

## Query The Registry

Use the bundled script to list sources:

```bash
python <base_dir>/scripts/list_sources.py --domain ai-tech
python <base_dir>/scripts/list_sources.py --domain economics --purpose macro-data --primary-only
python <base_dir>/scripts/list_sources.py --domain crypto --format markdown
```

Parameters:

| Parameter | Description |
|---|---|
| `--domain` | `ai-tech`, `crypto`, `economics`, `research`, or `cross-domain`. |
| `--purpose` | Optional filter such as `news`, `market-data`, `macro-data`, `papers`, `models`, `regulation`, `repos`. |
| `--primary-only` | Return only primary or official sources. |
| `--format` | `json` or `markdown`. |

The catalog lives at `references/sources.json`.

## Domain Defaults

Use these defaults when the user does not specify sources:

- AI technical brief: official model/company blogs, GitHub, arXiv, Papers with Code, specialist AI media.
- Crypto market brief: CoinGecko/market data, project official channels, exchange/regulatory sources, specialist crypto media.
- Economic analysis: FRED, BLS, BEA, central bank sites, treasury/yield sources, official statistical agencies.
- Company disclosure analysis: official investor-relations pages and regulatory filings before media summaries.
- Research/literature: arXiv, Semantic Scholar, OpenReview, publisher pages, GitHub/Papers with Code.

## Verification Rules

- Latest model/API claims: verify official provider docs or release notes.
- Prices, yields, macro prints, ETF flows, and policy decisions: verify current data before analysis.
- Crypto rumors: do not treat social posts as fact unless confirmed by official project, exchange, regulator, or reputable reporting.
- Research claims: cite paper, arXiv/OpenReview page, repo, or benchmark page. Label blog-only claims as interpretation.
- Cross-domain briefs: use one source set per involved domain and state any evidence gaps.

## Archiving

When a recurring brief uses a stable source mix, save the source list or source rationale under the related knowledge folder:

- `knowledge/ai-tech/sources/`
- `knowledge/crypto/sources/`
- `knowledge/economics/sources/`
- `knowledge/research/sources/`
- `knowledge/cross-domain/sources/`

Update `knowledge/index.md` and `knowledge/log.md` using `knowledge-wiki`.
