# Layered Memory Architecture

This document proposes a trainable layered memory architecture for ZVAgent.
The goal is to separate memory by lifecycle and update semantics, while keeping
runtime token cost controlled through lazy retrieval and asynchronous
consolidation.

## Goals

- Keep online conversation cheap: do not update every memory layer on every turn.
- Make memory training possible by storing structured extraction, scoring, and
  write-decision records.
- Separate user profile facts from general long-term memories.
- Use mid-term memory as a buffer before committing anything to profile or
  long-term memory.
- Keep retrieval infrastructure rebuildable; indexes are not the source of truth.

## Layers

```text
L0 Current working context
  In-process message window used by the model during the current run.

L1 Short-term session history
  SQLite session/message persistence for restoring recent conversations.

L2 Episodic mid-term memory
  Recent event-level memories extracted from conversations.

L3 Profile memory
  Structured user model: identity, preferences, goals, constraints, relationships,
  and communication style.

L4 Long-term semantic/procedural memory
  Stable facts, project decisions, procedures, reusable lessons, and durable
  knowledge.

L5 Retrieval infrastructure
  FTS, vector index, and optional graph index. These are derived from L2-L4 and
  can be rebuilt.
```

The memory "truth" lives in L2-L4. L5 is an acceleration layer.

## Proposed Workspace Layout

```text
workspace/
  memory/
    episodic/
      2026-06-03.jsonl
      compacted/
        2026-06-week-1.md

    profile/
      user_profile.json
      profile_summary.md
      profile_history.jsonl

    long_term/
      memory.md
      decisions.md
      procedures.md
      index.db
      graph.db

    jobs/
      compaction_queue.jsonl
      consolidation_log.jsonl
```

For backward compatibility, existing `MEMORY.md` can be treated as a legacy
long-term summary and gradually migrated into `memory/long_term/memory.md`.

## Episodic Memory Schema

Episodic memory is stored as JSONL so it can become training data later.

```json
{
  "id": "evt_20260603_001",
  "created_at": "2026-06-03T20:15:00+08:00",
  "source": "chat",
  "session_id": "web_xxx",
  "type": "discussion",
  "summary": "The user prefers a Hermes-style layered memory system with an explicit profile layer.",
  "entities": ["Hermes Agent", "ZVAgent", "profile memory"],
  "importance": 0.82,
  "stability": 0.65,
  "privacy": "normal",
  "candidate_targets": ["profile", "long_term"],
  "raw_refs": [
    {
      "message_seq_start": 42,
      "message_seq_end": 47
    }
  ]
}
```

Important fields:

- `importance`: whether the memory is worth keeping.
- `stability`: whether it is likely to remain true.
- `candidate_targets`: where consolidation may send it.
- `raw_refs`: provenance for audit and future training.

## Profile Memory Schema

Profile memory should be structured and conservative. It is a slow-changing
model of the user, not a log of events.

```json
{
  "identity": {
    "name": null,
    "timezone": "Asia/Shanghai",
    "language": "zh-CN"
  },
  "preferences": [
    {
      "id": "pref_memory_architecture_001",
      "key": "memory_architecture",
      "value": "Prefers Hermes-style layered memory with an explicit profile layer.",
      "confidence": 0.86,
      "evidence_ids": ["evt_20260603_001"],
      "created_at": "2026-06-03T20:15:00+08:00",
      "updated_at": "2026-06-03T20:15:00+08:00",
      "status": "active"
    }
  ],
  "goals": [
    {
      "id": "goal_memory_training_system",
      "value": "Build a system to train mid-term and long-term memory layers.",
      "confidence": 0.9,
      "status": "active",
      "evidence_ids": ["evt_20260603_002"]
    }
  ],
  "communication_style": {
    "prefers_language": "Chinese",
    "prefers_depth": "architecture-first, implementation-aware"
  }
}
```

A short `profile_summary.md` is generated from the JSON profile and can be
injected into the prompt by default. The full JSON is retrieved only when needed.

## Long-Term Memory

Long-term memory should be split by purpose:

- `memory.md`: stable facts and durable context.
- `decisions.md`: important project and architecture decisions.
- `procedures.md`: reusable workflows, lessons, and methods.

Example decision record:

```md
## 2026-06-03 - Use Mid-Term Buffer + Profile + Long-Term Memory

- Context: The user prefers Hermes Agent's explicit profile memory layer.
- Decision: Keep profile memory separate from general long-term memory.
- Reason: Structured profile memory supports conflict updates, confidence, and
  training data generation.
- Evidence: evt_20260603_001, evt_20260603_002
```

## Write Path

Online writing should remain lightweight:

```text
conversation/session trim
  -> episodic extractor
  -> scorer/router
  -> append episodic JSONL
  -> enqueue compaction or consolidation if thresholds are exceeded
```

Profile and long-term memory are updated asynchronously:

```text
episodic batch
  -> profile updater
  -> long-term consolidator
  -> compactor
  -> index rebuild
```

The system should avoid updating profile and long-term memory on every turn.

## Compression Thresholds

Initial defaults:

```json
{
  "episodic": {
    "max_items": 30,
    "max_tokens": 3000,
    "keep_recent_items": 8,
    "compact_target_tokens": 1000,
    "compact_interval_hours": 24
  },
  "profile": {
    "candidate_batch_size": 20,
    "min_confidence_to_write": 0.7,
    "conflict_check": true
  },
  "long_term": {
    "max_items": 80,
    "max_tokens": 8000,
    "compact_target_items": 40,
    "compact_interval_days": 3
  }
}
```

Episodic memory can be compressed aggressively. Profile and long-term memory
should be updated conservatively because mistakes affect many future turns.

## Read Path

Default prompt injection should be small:

```text
profile_summary.md       <= 300 tokens
long-term short summary  <= 500 tokens
```

Detailed memories are retrieved on demand:

- Recent or past-event questions -> episodic memory.
- Preference, habit, identity, goal questions -> profile memory.
- Architecture decisions and durable project facts -> long-term decisions.
- Methods and reusable workflows -> long-term procedures.

The retrieval router should return layer-specific top-k results, then rerank and
pack the final context under a fixed token budget.

## Training Data Hooks

Every extraction/consolidation pass should emit a training record:

```json
{
  "input_messages": [],
  "extracted_memories": [],
  "scores": {},
  "write_decision": {
    "episodic": true,
    "profile": false,
    "long_term": true
  },
  "retrieval_used_later": null,
  "user_feedback": null,
  "model_version": "memory-extractor-v1"
}
```

This enables future training of:

- Extractor: conversation -> candidate memories.
- Scorer: importance, stability, privacy, confidence.
- Router: episodic vs profile vs long-term destination.
- Consolidator: merge, deduplicate, conflict update, discard.
- Retriever: decide which layer to recall for a task.

## MVP Plan

1. Keep existing `ConversationStore` for session history.
2. Add episodic JSONL storage and basic append/query APIs.
3. Add profile JSON storage and generated profile summary.
4. Add layered memory config thresholds.
5. Add a compaction/consolidation service with conservative defaults.
6. Extend memory search to support layer filters.
7. Inject only profile summary and compact long-term summary by default.

The first milestone should focus on recording good structured memory data. More
advanced graph retrieval and learned routing can come later.
