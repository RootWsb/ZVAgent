import json
import os

import pytest

from cli.commands import skill_evolution as evo


def _make_skill(root, name="demo-skill", description="A demo skill for testing."):
    skill_dir = root / "skills" / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\nUse when testing.\n",
        encoding="utf-8",
    )
    return skill_dir


@pytest.fixture()
def isolated_evolution(tmp_path, monkeypatch):
    workspace = tmp_path / "zvagent"
    project = tmp_path / "project"
    builtin = project / "skills"
    workspace.mkdir()
    builtin.mkdir(parents=True)
    monkeypatch.setattr(evo, "get_workspace_dir", lambda: str(workspace))
    monkeypatch.setattr(evo, "get_skills_dir", lambda: str(workspace / "skills"))
    monkeypatch.setattr(evo, "get_builtin_skills_dir", lambda: str(builtin))
    monkeypatch.setattr(evo, "get_project_root", lambda: str(project))
    return workspace


def test_create_draft_and_validate(isolated_evolution):
    _make_skill(isolated_evolution, "demo-skill")

    draft = evo.create_draft("demo-skill")

    assert os.path.isdir(draft.proposal_dir)
    assert os.path.isfile(os.path.join(draft.editable_skill_dir, "SKILL.md"))
    assert evo.validate_skill_dir(draft.editable_skill_dir).ok

    meta_path = os.path.join(draft.proposal_dir, "proposal.json")
    meta = json.loads(open(meta_path, encoding="utf-8").read())
    assert meta["skill_name"] == "demo-skill"


def test_evolution_events_are_recorded_and_listed(isolated_evolution):
    first = evo.record_event("first_action", skill_name="demo-skill", detail="one")
    second = evo.record_event("second_action", skill_name="demo-skill", detail="two")

    events = evo.list_events(limit=10)

    assert events[0]["event_id"] == second["event_id"]
    assert events[1]["event_id"] == first["event_id"]
    assert events[0]["details"]["detail"] == "two"


def test_create_draft_records_event(isolated_evolution):
    _make_skill(isolated_evolution, "demo-skill")

    draft = evo.create_draft("demo-skill")
    events = evo.list_events(limit=5)

    assert events[0]["action"] == "draft_created"
    assert events[0]["proposal_id"] == draft.proposal_id
    assert events[0]["skill_name"] == "demo-skill"


def test_analyze_skill_usage_filters_matching_logs(isolated_evolution, monkeypatch):
    _make_skill(isolated_evolution, "demo-skill")
    monkeypatch.setattr(
        evo,
        "_load_skill_usage_logs",
        lambda limit=200: [
            {
                "tool_name": "demo-skill",
                "status": "success",
                "user_message": "Summarize this document",
                "result": "ok",
                "execution_time": 1.2,
            },
            {
                "tool_name": "other-skill",
                "status": "failed",
                "user_message": "not relevant",
                "result": "boom",
                "execution_time": 0.1,
            },
            {
                "tool_name": "demo-skill",
                "status": "failed",
                "user_message": "demo-skill failed case",
                "result": "missing input",
                "execution_time": 12,
            },
        ],
    )

    evidence = evo.analyze_skill_usage("demo-skill")

    assert evidence["matched_count"] == 2
    assert evidence["failure_count"] == 1
    assert evidence["slow_count"] == 1
    assert "Summarize this document" in evidence["sample_prompts"]


def test_score_skills_prioritizes_low_health(isolated_evolution, monkeypatch):
    _make_skill(isolated_evolution, "healthy-skill")
    _make_skill(isolated_evolution, "weak-skill")
    monkeypatch.setattr(
        evo,
        "_load_skill_usage_logs",
        lambda limit=500: [
            {
                "tool_name": "healthy-skill",
                "status": "success",
                "execution_time": 1,
                "created_at": 10,
            },
            {
                "tool_name": "weak-skill",
                "status": "failed",
                "execution_time": 12,
                "created_at": 20,
            },
            {
                "tool_name": "weak-skill",
                "status": "success",
                "execution_time": 13,
                "created_at": 21,
            },
        ],
    )

    scores = evo.score_skills(["healthy-skill", "weak-skill"])
    by_name = {item["skill_name"]: item for item in scores}

    assert by_name["weak-skill"]["score"] < by_name["healthy-skill"]["score"]
    assert by_name["weak-skill"]["priority"] in {"medium", "high"}
    assert scores[0]["skill_name"] == "weak-skill"


def test_auto_learn_queue_creates_for_low_health_skills(isolated_evolution, monkeypatch):
    _make_skill(isolated_evolution, "healthy-skill")
    _make_skill(isolated_evolution, "weak-skill")
    monkeypatch.setattr(
        evo,
        "_load_skill_usage_logs",
        lambda limit=500: [
            {
                "tool_name": "healthy-skill",
                "status": "success",
                "execution_time": 1,
                "created_at": 10,
                "user_message": "healthy",
            },
            {
                "tool_name": "weak-skill",
                "status": "failed",
                "execution_time": 12,
                "created_at": 20,
                "user_message": "weak failed",
                "result": "missing input",
            },
        ],
    )

    queued = evo.create_auto_learn_queue(["healthy-skill", "weak-skill"], max_items=2)

    assert len(queued["created"]) == 1
    assert queued["created"][0]["skill_name"] == "weak-skill"
    proposals = evo.list_proposals("weak-skill")
    assert proposals[0]["mode"] == "auto_learn"


def test_auto_learn_queue_skips_existing_pending_auto_proposal(isolated_evolution, monkeypatch):
    _make_skill(isolated_evolution, "weak-skill")
    monkeypatch.setattr(
        evo,
        "_load_skill_usage_logs",
        lambda limit=500: [
            {
                "tool_name": "weak-skill",
                "status": "failed",
                "execution_time": 12,
                "created_at": 20,
                "user_message": "weak failed",
                "result": "missing input",
            },
        ],
    )

    first = evo.create_auto_learn_queue(["weak-skill"], max_items=2)
    second = evo.create_auto_learn_queue(["weak-skill"], max_items=2)

    assert len(first["created"]) == 1
    assert len(second["created"]) == 0
    assert second["skipped"][0]["reason"] == "pending_auto_proposal"


def test_auto_learn_proposal_updates_skill_copy(isolated_evolution, monkeypatch):
    _make_skill(isolated_evolution, "demo-skill")
    monkeypatch.setattr(
        evo,
        "_load_skill_usage_logs",
        lambda limit=200: [
            {
                "tool_name": "demo-skill",
                "status": "failed",
                "user_message": "Please use demo-skill with missing input",
                "result": "missing required input",
                "execution_time": 2,
            }
        ],
    )

    draft = evo.create_auto_learn_proposal("demo-skill")
    skill_md = os.path.join(draft.editable_skill_dir, "SKILL.md")
    content = open(skill_md, encoding="utf-8").read()

    assert "## Auto-Learned Usage Notes" in content
    assert "Please use demo-skill with missing input" in content
    assert os.path.isfile(os.path.join(draft.proposal_dir, "evidence.json"))
    assert evo.validate_skill_dir(draft.editable_skill_dir).ok


def test_get_proposal_diff_shows_changes(isolated_evolution):
    _make_skill(isolated_evolution, "demo-skill")
    draft = evo.create_draft("demo-skill")
    skill_md = os.path.join(draft.editable_skill_dir, "SKILL.md")
    with open(skill_md, "a", encoding="utf-8") as f:
        f.write("\nDiff preview behavior.\n")

    diff = evo.get_proposal_diff(draft.proposal_id)

    assert diff["proposal_id"] == draft.proposal_id
    assert diff["skill_name"] == "demo-skill"
    assert len(diff["files"]) == 1
    assert diff["files"][0]["path"] == "SKILL.md"
    assert "+Diff preview behavior." in diff["files"][0]["diff"]


def test_replay_auto_learn_proposal_checks_evidence(isolated_evolution, monkeypatch):
    _make_skill(isolated_evolution, "demo-skill")
    monkeypatch.setattr(
        evo,
        "_load_skill_usage_logs",
        lambda limit=200: [
            {
                "tool_name": "demo-skill",
                "status": "failed",
                "user_message": "Please run demo-skill with a source file",
                "result": "missing source file",
                "execution_time": 3,
            }
        ],
    )
    draft = evo.create_auto_learn_proposal("demo-skill")

    result = evo.replay_proposal(draft.proposal_id)

    assert result["proposal_id"] == draft.proposal_id
    assert result["summary"]["total"] >= 4
    assert result["summary"]["failed"] == 0
    proposals = evo.list_proposals("demo-skill")
    assert proposals[0]["last_replay"]["summary"]["total"] == result["summary"]["total"]


def test_replay_manual_proposal_reports_missing_guidance(isolated_evolution):
    _make_skill(isolated_evolution, "demo-skill", description="short")
    draft = evo.create_draft("demo-skill")

    result = evo.replay_proposal(draft.proposal_id)

    failed_ids = {item["id"] for item in result["checks"] if item["status"] == "failed"}
    assert "input-guidance" in failed_ids
    assert "output-guidance" in failed_ids


def test_ai_rewrite_proposal_updates_copy_and_creates_backup(isolated_evolution, monkeypatch):
    _make_skill(isolated_evolution, "demo-skill")
    monkeypatch.setattr(evo, "_load_skill_usage_logs", lambda limit=200: [])
    draft = evo.create_draft("demo-skill")

    def fake_llm(_prompt):
        return """---
name: demo-skill
description: A better demo skill with clear trigger conditions and fallback behavior.
---

## When to use
Use when testing skill evolution behavior.

## Inputs
- Provide a clear test request.

## Output
Return a concise test result.

## Failure handling
If required input is missing, ask for it and provide a fallback.
"""

    result = evo.ai_rewrite_proposal(draft.proposal_id, llm_callable=fake_llm)
    content = open(os.path.join(draft.editable_skill_dir, "SKILL.md"), encoding="utf-8").read()

    assert result["validation"]["ok"]
    assert os.path.isfile(result["backup_path"])
    assert "A better demo skill" in content
    assert result["replay"]["summary"]["failed"] == 0
    proposal = evo.list_proposals("demo-skill")[0]
    assert proposal["status"] == "ai_rewritten"
    assert proposal["last_ai_rewrite"]["validation"]["ok"]


def test_ai_rewrite_rejects_skill_name_change(isolated_evolution):
    _make_skill(isolated_evolution, "demo-skill")
    draft = evo.create_draft("demo-skill")

    def fake_llm(_prompt):
        return "---\nname: other-skill\ndescription: bad\n---\n\n## When to use\nNever.\n"

    with pytest.raises(evo.SkillEvolutionError):
        evo.ai_rewrite_proposal(draft.proposal_id, llm_callable=fake_llm)


def test_auto_apply_safe_applies_only_safe_skill_md_change(isolated_evolution, monkeypatch):
    live_dir = _make_skill(isolated_evolution, "demo-skill")
    monkeypatch.setattr(
        evo,
        "_load_skill_usage_logs",
        lambda limit=200: [
            {
                "tool_name": "demo-skill",
                "status": "failed",
                "user_message": "Please run demo-skill with a source file",
                "result": "missing source file",
                "execution_time": 2,
            }
        ],
    )
    draft = evo.create_auto_learn_proposal("demo-skill")

    evaluation = evo.evaluate_safe_apply(draft.proposal_id)
    result = evo.auto_apply_safe(max_items=1)

    assert evaluation["safe"]
    assert len(result["applied"]) == 1
    assert result["applied"][0]["skill_name"] == "demo-skill"
    assert "Auto-Learned Usage Notes" in (live_dir / "SKILL.md").read_text(encoding="utf-8")


def test_auto_apply_safe_skips_script_changes(isolated_evolution):
    _make_skill(isolated_evolution, "demo-skill")
    draft = evo.create_draft("demo-skill")
    scripts_dir = os.path.join(draft.editable_skill_dir, "scripts")
    os.makedirs(scripts_dir)
    with open(os.path.join(scripts_dir, "tool.py"), "w", encoding="utf-8") as f:
        f.write("print('changed')\n")
    meta_path = os.path.join(draft.proposal_dir, "proposal.json")
    meta = json.loads(open(meta_path, encoding="utf-8").read())
    meta.update({"status": "auto_learned", "mode": "auto_learn"})
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)

    evaluation = evo.evaluate_safe_apply(draft.proposal_id)
    result = evo.auto_apply_safe(max_items=1)

    assert not evaluation["safe"]
    assert "safe auto-apply only allows a single SKILL.md change" in evaluation["reasons"]
    assert len(result["applied"]) == 0


def test_run_evolution_cycle_queues_rewrites_and_applies(isolated_evolution, monkeypatch):
    live_dir = _make_skill(isolated_evolution, "weak-skill")
    monkeypatch.setattr(
        evo,
        "_load_skill_usage_logs",
        lambda limit=500: [
            {
                "tool_name": "weak-skill",
                "status": "failed",
                "execution_time": 12,
                "created_at": 20,
                "user_message": "Please run weak-skill with a source file",
                "result": "missing source file",
            },
        ],
    )

    def fake_llm(_prompt):
        return """---
name: weak-skill
description: A better weak skill with clear trigger conditions and fallback behavior.
---

## When to use
Use when testing weak-skill evolution behavior.

## Inputs
- Provide a source file or clear input data.

## Output
Return a concise result with any assumptions.

## Failure handling
If input is missing or invalid, ask for the missing input and provide a fallback.
"""

    result = evo.run_evolution_cycle(["weak-skill"], max_queue=1, max_apply=1, llm_callable=fake_llm)
    content = (live_dir / "SKILL.md").read_text(encoding="utf-8")
    events = evo.list_events(limit=20)

    assert result["summary"]["queued"] == 1
    assert result["summary"]["rewritten"] == 1
    assert result["summary"]["applied"] == 1
    assert "A better weak skill" in content
    assert any(event["action"] == "cycle_completed" for event in events)


def test_apply_and_rollback_proposal(isolated_evolution):
    live_dir = _make_skill(isolated_evolution, "demo-skill")
    draft = evo.create_draft("demo-skill")
    skill_md = os.path.join(draft.editable_skill_dir, "SKILL.md")
    with open(skill_md, "a", encoding="utf-8") as f:
        f.write("\nNew behavior.\n")

    applied = evo.apply_proposal(draft.proposal_id)

    assert os.path.isdir(applied.backup_dir)
    assert "New behavior." in (live_dir / "SKILL.md").read_text(encoding="utf-8")

    rolled = evo.rollback_skill("demo-skill", backup_id=applied.backup_id)

    assert rolled.backup_id == applied.backup_id
    assert "New behavior." not in (live_dir / "SKILL.md").read_text(encoding="utf-8")


def test_rejects_unsafe_skill_name(isolated_evolution):
    with pytest.raises(evo.SkillEvolutionError):
        evo.create_draft("../bad")
