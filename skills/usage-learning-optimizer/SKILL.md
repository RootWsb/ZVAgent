---
name: usage-learning-optimizer
description: Maintain a lightweight usage-learning layer that makes this vertical assistant more personalized and token-efficient over time. Use when the user gives feedback, asks the agent to remember preferences, wants shorter or smarter answers, asks to reduce token usage, asks to improve recurring workflows, or when a completed task reveals reusable preferences, task patterns, context budgets, or domain-specific output habits.
---

# Usage Learning Optimizer

Use this skill to turn repeated use into reusable guidance without bloating the prompt.

## Principle

Do not store full conversations. Store compact, reusable rules:

- user preferences
- recurring task patterns
- output length and evidence budgets
- feedback that changes future behavior
- short context packs for the current task

Prefer small files under `knowledge/profile/` over long memory dumps.

## Files

Maintain these files in the workspace:

- `knowledge/profile/user_preferences.md`: stable user preferences and domain tastes.
- `knowledge/profile/task_patterns.md`: reusable task templates and routing hints.
- `knowledge/profile/context_budget.md`: answer modes, retrieval depth, and token-saving rules.
- `knowledge/profile/feedback_log.md`: append-only raw feedback.
- `knowledge/profile/template_evolution.md`: accepted feedback-driven changes.
- `knowledge/profile/proposals/`: pending template/preference proposals.

Use `scripts/learning_memory.py init --workspace <workspace>` to create them safely.

## Workflow

### 1. Before Repeated Or Personalized Work

If the user asks for recurring analysis, a familiar domain, or "按我的习惯", build a compact context pack:

```bash
python skills/usage-learning-optimizer/scripts/learning_memory.py context --domain ai-tech --task-type paper --workspace .
```

Read only the generated output or the specific profile file you need. Do not read every old note.

### 2. When User Gives Feedback

Examples:

- "以后短一点"
- "AI 论文都加工程复现性"
- "加密货币分析别给买卖建议，重点说风险"
- "这个结构不错，记下来"

Record it:

```bash
python skills/usage-learning-optimizer/scripts/learning_memory.py feedback --feedback "AI 论文都加工程复现性" --domain ai-tech --task-type paper --workspace .
```

Then update `user_preferences.md`, `task_patterns.md`, or `context_budget.md` only if the feedback should affect future behavior.

For feedback that should change future behavior, use `feedback-template-evolver` to create a reviewable proposal before applying permanent changes.

### 3. Mode Selection

Default to the smallest sufficient mode:

| Mode | Use for | Target |
|---|---|---|
| `quick` | direct questions, already-known topics | <= 300 Chinese chars or 5 bullets |
| `brief` | normal analysis and daily use | 600-1200 Chinese chars |
| `deep` | explicit deep dives, reviews, strategy | structured long answer |
| `archive` | durable notes for `knowledge/` | concise but complete Markdown page |

Use:

```bash
python skills/usage-learning-optimizer/scripts/learning_memory.py mode --prompt "<user request>"
```

### 4. Token-Saving Rules

- Check profile/context first for repeated workflows.
- Reuse existing templates instead of inventing structure each time.
- Summarize old knowledge before adding new detail.
- Use `knowledge-compression-indexer` when many old notes are relevant.
- Prefer links to local knowledge pages over restating entire notes.
- For current facts, fetch only the sources needed for the claim.
- For long tasks, deliver a short conclusion first, then archive detail only when useful.

## Updating Knowledge

After creating or changing profile files:

1. Update `knowledge/index.md` with the profile pages if missing.
2. Append a short line to `knowledge/log.md`.
3. Keep entries short. If a preference conflicts with a newer explicit user request, the newer request wins.
4. For reusable changes, prefer the proposal/apply loop in `feedback-template-evolver`.
