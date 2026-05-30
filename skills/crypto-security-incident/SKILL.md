---
name: crypto-security-incident
description: Crypto security incident analysis workflow for hacks, exploits, bridge failures, oracle attacks, key compromises, smart-contract bugs, exchange incidents, depegs, protocol pauses, emergency governance, and post-mortems. Use when the user asks what happened in a crypto attack or operational incident, which assets or protocols are affected, whether funds are at risk, or how an incident changes project and market risk.
---

# Crypto Security Incident

## Overview

Use this skill to triage security events without amplifying rumors. Produce a fact-first incident memo with timeline, mechanism, impact, response, contagion risk, and unresolved facts.

Prefer Chinese unless the user asks otherwise. Use `source-registry`, `crypto-news`, and `surf` when current evidence or on-chain context is needed.

## Workflow

1. Confirm the event from project statements, explorer evidence, auditors/security researchers, exchange or regulator notices, and reputable specialist reporting.
2. Build a timeline: detection, exploit transactions, protocol response, pause or upgrade, recovery, and post-mortem.
3. Classify the failure mode: contract bug, oracle manipulation, bridge issue, key compromise, governance attack, frontend/DNS issue, liquidity attack, custody or exchange operation, stablecoin depeg.
4. Identify affected chains, assets, contracts, pools, users, and counterparties.
5. Estimate losses and recovery status. Mark numbers as preliminary when sources disagree.
6. Map contagion channels: token price, TVL, collateral, lending markets, bridge exposure, exchange withdrawals, ecosystem trust.
7. End with unresolved facts and monitoring triggers.

## Incident Labels

- `confirmed`: official statement or clear primary evidence.
- `likely`: multiple credible sources but incomplete primary confirmation.
- `rumor`: social-only or anonymous. Do not present as fact.
- `ongoing`: exploit, pause, recovery, or investigation still active.

## Output Shape

```markdown
# Crypto Security Incident: <event>

## Status
- Label:
- Time window:
- Affected systems:

## What Happened
...

## Mechanism
...

## Impact
- Loss estimate:
- Market/liquidity:
- Contagion paths:

## Response And Recovery
...

## Unresolved Facts
- ...

## Monitoring
- ...
```

Never invent contract addresses, recovery forms, revoke links, or wallet instructions. Verify official guidance before discussing operational user actions.
