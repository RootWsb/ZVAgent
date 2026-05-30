---
name: feedback-template-evolver
description: Close the learning loop by turning user feedback into reviewable changes to preferences, task patterns, and token budgets. Use when the user says future answers should change, likes or dislikes an output structure, asks to remember a template, says an answer is too long or too short, or wants recurring workflows to evolve from feedback.
---

# Feedback Template Evolver

Use this skill to evolve the assistant without bloating prompts.

## Core Idea

Do not immediately turn every comment into a permanent rule. Use a two-step loop:

1. Record feedback and generate a proposal.
2. Apply the proposal only when it is stable, explicit, or confirmed by the user.

This keeps the assistant adaptive without overfitting to one conversation.

## Files

This skill works with `usage-learning-optimizer` profile files:

- `knowledge/profile/user_preferences.md`
- `knowledge/profile/task_patterns.md`
- `knowledge/profile/context_budget.md`
- `knowledge/profile/feedback_log.md`

It also creates:

- `knowledge/profile/template_evolution.md`
- `knowledge/profile/proposals/<proposal-id>.md`

## Commands

Initialize the feedback loop:

```bash
python skills/feedback-template-evolver/scripts/evolve_templates.py init --workspace .
```

Create a proposal from feedback:

```bash
python skills/feedback-template-evolver/scripts/evolve_templates.py propose --workspace . --feedback "以后 AI 论文总结都加工程复现性" --domain ai-tech --task-type paper
```

One feedback item may generate multiple proposals when it contains multiple durable changes, such as both an output-length rule and a domain preference.

List pending proposals:

```bash
python skills/feedback-template-evolver/scripts/evolve_templates.py list --workspace .
```

Apply a proposal after review:

```bash
python skills/feedback-template-evolver/scripts/evolve_templates.py apply --workspace . --proposal <proposal-id>
```

## Proposal Rules

Create a proposal when feedback contains:

- "以后", "下次", "默认", "总是", "记住"
- "这个结构不错", "保留这个模板"
- "太长", "太短", "简短", "详细"
- domain-specific durable preferences

Do not apply automatically when:

- the user is only reacting emotionally
- the request conflicts with existing stronger rules
- the feedback is one-off or task-specific

## Target Selection

- Output length/depth feedback -> `context_budget.md`
- Domain taste or stable habit -> `user_preferences.md`
- Output structure/template -> `task_patterns.md`
- Raw feedback history -> `feedback_log.md`

## Application Discipline

- Append short bullets; do not rewrite whole files.
- Preserve newer explicit user instructions over older preferences.
- Avoid duplicate bullets.
- Update `knowledge/log.md` after applying.
- If unsure, show the proposal and ask before applying.
