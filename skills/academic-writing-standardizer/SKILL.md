---
name: academic-writing-standardizer
description: Academic writing standardization workflow for research papers, abstracts, introductions, related work, methods, experiment sections, limitations, rebuttals, proposals, thesis chapters, and grant-style drafts. Use when the user asks to polish academic writing, make a draft more rigorous, improve argument structure, reduce vague claims, align with paper style, rewrite Chinese academic text, translate between Chinese and English academic prose, or prepare publication-ready sections.
---

# Academic Writing Standardizer

## Overview

Use this skill to improve academic clarity, rigor, and structure without changing the research claim. Preserve the user's intended meaning and mark places where evidence is missing.

Prefer Chinese unless the user requests English. For citations and bibliography metadata, use `citation-management` or `evidence-citation-writer`.

## Workflow

1. Identify the target section: abstract, introduction, related work, method, experiment, result, discussion, limitation, rebuttal, proposal, or thesis chapter.
2. Preserve claims, variables, numbers, citations, and terminology. Do not invent results, baselines, or citations.
3. Improve argument order: problem -> gap -> method -> evidence -> implication.
4. Replace vague language with precise claims and scope conditions.
5. Add transition sentences only when they clarify logic.
6. Flag unsupported claims as `[needs evidence]` rather than silently strengthening them.
7. Keep equations, symbols, citations, and code identifiers unchanged unless the user asks to revise them.
8. For method, experiment, result, discussion, thesis, or technical-report sections, preserve valid equations and recommend a compact quantitative framework when the argument depends on variables, objectives, estimands, metrics, or statistical comparisons.
9. When the document is an analytical report rather than a text-only rewrite, include or recommend figure/table placements that make the evidence easier to inspect: method diagrams, experimental setup diagrams, main-result charts, ablation tables, uncertainty plots, or comparison matrices.
10. Never invent numeric figures, captions, citations, or results. Use explicit placeholders such as `[insert verified ablation plot here]` when the underlying data or file is unavailable.

## Section Patterns

- Abstract: background, gap, method, key result, implication.
- Introduction: motivation, limitation of existing work, contribution bullets, paper roadmap.
- Related work: organize by method family; compare deltas rather than listing papers.
- Method: define inputs, outputs, assumptions, modules, objective, and inference path.
- Experiment: datasets, baselines, metrics, setup, main results, ablations, limitations.
- Limitations: scope, assumptions, failure modes, compute/data constraints, ethical risks.

## Quantitative And Exhibit Guidance

When improving a complete academic analysis report, ensure that presentation supports the argument:

- Put key objective functions, metrics, or estimands in display-math form and define all symbols.
- Use figures/tables only where they support a claim: pipeline overview, baseline comparison, main result, ablation, or error analysis.
- If an exhibit is available, provide a source-aware caption: what is plotted, dataset/timeframe, metric/unit, and the conclusion supported.
- For conceptual diagrams, prefer fenced Mermaid blocks that render directly in the web UI. If a visual must be newly generated from verified values, save it to a workspace-backed `figures/` path and link it with Markdown after confirming the file exists.
- Place figures and tables immediately after the claim, method component, experiment result, or limitation they support. Do not collect unrelated visuals into one block unless writing a dedicated figure appendix.
- For generated visuals, use a restrained academic-console style: dark or transparent background, compact labels, thin borders, and no decorative poster treatment.

## Output Shape

When editing a draft, return:

```markdown
## Revised Draft
...

## Major Changes
- ...

## Claims Needing Evidence
- ...

## Optional Stronger Version
...
```

If the user only wants a direct rewrite, provide the revised draft first and keep notes short.
