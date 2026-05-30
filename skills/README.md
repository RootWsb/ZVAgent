# Skills

Skills are reusable instruction sets that extend the agent's capabilities. Each skill is a `SKILL.md` file in its own directory, providing specialized knowledge, workflows, and tool integrations for specific tasks.

## Skill Hub

Browse, search, and install skills from [ZV Skill Hub](https://skills.zvagent.ai/).

Open source: [github.com/zhayujie/zv-skill-hub](https://github.com/zhayujie/zv-skill-hub)

## Install Skills

Install skills from multiple sources via chat (`/skill`) or terminal (`zv skill`):

```bash
/skill install <name>                   # From Skill Hub
/skill install <owner>/<repo>           # From GitHub
/skill install clawhub:<name>           # From ClawHub
/skill install linkai:<code>            # From LinkAI
/skill install <url>                    # From URL (zip or SKILL.md)
```

List all available remote skills:

```bash
/skill list --remote
```

## Manage Skills

```bash
/skill list                  # List installed skills
/skill info <name>           # View skill details
/skill enable <name>         # Enable a skill
/skill disable <name>        # Disable a skill
/skill uninstall <name>      # Uninstall a skill
```

> In terminal, replace `/skill` with `zv skill`.

## Built-in Vertical Skills

This project includes a first set of domain skills for a research-oriented assistant:

- `vertical-research-orchestrator`: routes open-ended or cross-domain requests to the right specialized workflow.
- `task-budget-router`: chooses quick/brief/deep/archive mode, retrieval depth, output budget, and required skills.
- `brief-automation`: schedules, drafts, and archives recurring vertical research briefs.
- `source-registry`: selects trusted sources for evidence-sensitive vertical research.
- `quality-guardrails`: validates brief structure, sources, risk framing, and archive readiness.
- `academic-writing-standardizer`: standardizes academic prose, paper sections, proposals, thesis chapters, and rebuttals.
- `evidence-citation-writer`: turns drafts into source-grounded writing with evidence maps, claim labels, and citation discipline.
- `market-report-writer`: structures crypto, macro, financial, and due-diligence notes into professional reports.
- `ai-technical-writing`: writes AI technical explainers, model notes, repo summaries, and benchmark writeups.
- `knowledge-note-standardizer`: normalizes durable Markdown notes, tags, source sections, and backlinks.
- `usage-learning-optimizer`: maintains user preferences, recurring task patterns, feedback logs, and token budgets.
- `feedback-template-evolver`: turns user feedback into reviewable preference/template/budget updates.
- `knowledge-compression-indexer`: scans, maps, deduplicates, and compacts the knowledge base for lower token usage.
- `research-assistant`: paper reading, literature notes, code reproduction, experiment planning, and paper-code alignment.
- `language-learning`: daily language lessons, conversation practice, writing correction, mistake tracking, graded reading, and study plans.
- `paper-download`: downloads legal open-access paper PDFs from DOI, arXiv, PMCID, and direct PDF links.
- `research-hypothesis-planner`: turns early research ideas into questions, hypotheses, baselines, and study plans.
- `experiment-design-reviewer`: reviews experiment plans, metrics, ablations, validity, and reproducibility risks.
- `crypto-news`: crypto market briefs, asset deep dives, event analysis, and risk review.
- `token-due-diligence`: project and token fundamentals, tokenomics, unlocks, value capture, and red flags.
- `crypto-security-incident`: hack/exploit/depeg incident timeline, mechanism, impact, and recovery review.
- `economic-analysis`: macro data, central bank policy, cross-asset attribution, and economic briefs.
- `financial-news-impact`: market transmission and scenario analysis for financial news shocks.
- `earnings-filing-reader`: reads earnings, guidance, filings, and disclosure changes.
- `ai-tech-digest`: AI technical articles, model updates, repositories, papers, and daily/weekly digests.
- `ai-benchmark-auditor`: audits benchmark claims, leaderboards, eval fairness, and contamination risk.
- `ai-open-source-evaluator`: evaluates AI repositories for maturity, reproducibility, and adoption risk.
- `knowledge-wiki`: persistent knowledge capture across the four domains.

## Installed External Skills

The following GitHub skills were selected and installed for the four vertical domains. Risky capabilities are constrained by local safety notes in the relevant `SKILL.md` files.

| Domain | Skill | Source | Purpose |
|---|---|---|---|
| Research | `paper-lookup` | `K-Dense-AI/scientific-agent-skills` | arXiv, PubMed, Semantic Scholar, OpenAlex, Crossref, CORE, Unpaywall, DOI/PMID lookup. |
| Research | `paper-download` | Built-in | Legal open-access paper PDF downloads from DOI, arXiv, PMCID, and direct PDF links. |
| Research | `literature-review` | `K-Dense-AI/scientific-agent-skills` | systematic literature review, multi-paper synthesis, gap analysis. |
| Research | `citation-management` | `K-Dense-AI/scientific-agent-skills` | citation validation, BibTeX generation, DOI metadata cleanup. |
| Economics | `usfiscaldata` | `K-Dense-AI/scientific-agent-skills` | U.S. Treasury Fiscal Data API, debt, DTS/MTS, auctions, rates, FX. |
| Economics | `statistical-analysis` | `K-Dense-AI/scientific-agent-skills` | statistical tests, assumptions, diagnostics, reporting standards. |
| AI Tech | `huggingface-papers` | `huggingface/skills` | HF paper pages, arXiv IDs, linked models/datasets/spaces/repos. |
| AI Tech | `huggingface-datasets` | `huggingface/skills` | read-only Dataset Viewer workflows for dataset metadata, rows, search, filters, stats. |
| Cross Domain | `apify-ultimate-scraper` | `apify/agent-skills` | cross-platform web scraping for trend, review, social, market, and RAG data gathering. |
| Crypto | `surf` | `asksurf-ai/surf-skills` | read-only crypto market, token, on-chain, social, project, fund, and prediction-market data. |

Default analysis outputs share the same contract: `结论` → `依据` → `机制` → `风险/不确定性` → `下一步`. Domain-specific templates override this only when a more specialized note, brief, reproduction plan, or digest is needed.

## Skill Structure

```
skills/
  my-skill/
    SKILL.md          # Required: skill definition
    scripts/          # Optional: bundled scripts
    resources/        # Optional: reference files
```

`SKILL.md` uses YAML frontmatter:

```markdown
---
name: my-skill
description: Brief description of what the skill does
metadata: {"zvagent":{"emoji":"🔧","requires":{"bins":["tool"],"env":["API_KEY"]}}}
---

# My Skill

Instructions, examples, and usage patterns...
```

### Frontmatter Fields

| Field | Description |
|---|---|
| `name` | Skill name (must match directory name) |
| `description` | Brief description (required) |
| `metadata.zvagent.emoji` | Display emoji |
| `metadata.zvagent.always` | Always include this skill (default: false) |
| `metadata.zvagent.requires.bins` | Required binaries |
| `metadata.zvagent.requires.env` | Required environment variables |
| `metadata.zvagent.requires.config` | Required config paths |
| `metadata.zvagent.os` | Supported OS (e.g., `["darwin", "linux"]`) |

## Skill Loading Order

Skills are loaded from two locations (higher precedence overrides lower):

1. **Builtin skills** (lower): `<project_root>/skills/` — shipped with the codebase
2. **Custom skills** (higher): `~/zvagent/skills/` — installed via `zv skill install` or skill creator

Skills with the same name in the custom directory override builtin ones.

## Create & Contribute

See the [Skill Creation docs](https://docs.zvagent.ai/skills/create) for details, or submit your skill to [Skill Hub](https://skills.zvagent.ai/submit).
