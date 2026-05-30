import json

import pytest
from click.testing import CliRunner

from agent.skills.summary import write_skill_summary
from agent.skills.summary_generator import (
    SkillSummaryGenerationError,
    generate_skill_summary,
)
import cli.commands.skill as skill_commands


SKILL_CONTENT = """---
name: demo-skill
description: Demo workflow skill.
---

Use this skill for demo workflow requests.
Avoid using this skill for database migrations.
Required input: repo path and task goal.
Read the skill, inspect scripts, then run the workflow.
Use tools: read and bash.
Do not skip the validation step.
"""


class DummyModel:
    def __init__(self, payload):
        self.payload = payload
        self.calls = 0

    def call(self, request):
        self.calls += 1
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(self.payload, ensure_ascii=False),
                    }
                }
            ]
        }


def _valid_payload():
    return {
        "level_1": {
            "name": "demo-skill",
            "description": "Use this skill for demo workflow triage.",
            "tags": ["demo", "workflow"],
        },
        "level_2": {
            "one_line": "Use this skill for demo workflow requests.",
            "use_when": ["Demo workflow requests."],
            "avoid_when": ["Database migrations."],
            "prerequisites": ["Have a repo path and task goal."],
            "key_inputs": ["repo path", "task goal"],
            "workflow_outline": ["Read the skill, inspect scripts, then run the workflow."],
            "tool_dependencies": ["read", "bash"],
            "risk_flags": ["Do not skip the validation step."],
        },
        "evidence": {
            "use_when": ["Use this skill for demo workflow requests."],
            "avoid_when": ["Avoid using this skill for database migrations."],
            "prerequisites": ["Required input: repo path and task goal."],
            "key_inputs": ["Required input: repo path and task goal."],
            "workflow_outline": ["Read the skill, inspect scripts, then run the workflow."],
            "tool_dependencies": ["Use tools: read and bash."],
            "risk_flags": ["Do not skip the validation step."],
        },
    }


def _write_skill(tmp_path):
    skill_dir = tmp_path / "demo-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(SKILL_CONTENT, encoding="utf-8")
    return skill_dir


def test_generate_skill_summary_builds_valid_artifact(tmp_path):
    skill_dir = _write_skill(tmp_path)
    model = DummyModel(_valid_payload())

    result = generate_skill_summary(
        str(skill_dir),
        llm_model=model,
        provider="openai",
        model_name="gpt-test",
        generated_at="2026-05-21T10:00:00Z",
    )

    assert result.artifact is not None
    assert result.artifact.skill_name == "demo-skill"
    assert result.artifact.generator.provider == "openai"
    assert result.artifact.generator.model == "gpt-test"
    assert result.artifact.level_2.one_line == "Use this skill for demo workflow requests."
    assert result.validation is not None
    assert result.validation.ok
    assert model.calls == 1


def test_generate_skill_summary_skips_when_hash_is_unchanged(tmp_path):
    skill_dir = _write_skill(tmp_path)
    model = DummyModel(_valid_payload())
    first = generate_skill_summary(
        str(skill_dir),
        llm_model=model,
        provider="openai",
        model_name="gpt-test",
        generated_at="2026-05-21T10:00:00Z",
    )
    write_skill_summary(str(skill_dir / "SKILL.summary.json"), first.artifact)

    class ExplodingModel:
        def call(self, request):
            raise AssertionError("model should not be called when summary is unchanged")

    second = generate_skill_summary(
        str(skill_dir),
        llm_model=ExplodingModel(),
        provider="openai",
        model_name="gpt-test",
    )

    assert second.skipped
    assert second.skip_reason == "up-to-date"


def test_generate_skill_summary_rejects_ungrounded_payload(tmp_path):
    skill_dir = _write_skill(tmp_path)
    payload = _valid_payload()
    payload["evidence"]["risk_flags"] = ["This sentence does not exist in the source."]
    model = DummyModel(payload)

    with pytest.raises(SkillSummaryGenerationError, match="validation failed"):
        generate_skill_summary(
            str(skill_dir),
            llm_model=model,
            provider="openai",
            model_name="gpt-test",
        )


def test_resolve_summary_targets_prefers_custom_over_builtin(tmp_path, monkeypatch):
    builtin_dir = tmp_path / "builtin"
    custom_dir = tmp_path / "custom"
    _write_skill(builtin_dir)
    _write_skill(custom_dir)

    monkeypatch.setattr(skill_commands, "get_builtin_skills_dir", lambda: str(builtin_dir))
    monkeypatch.setattr(skill_commands, "get_skills_dir", lambda: str(custom_dir))

    targets = skill_commands._resolve_summary_targets(
        None,
        include_builtin=True,
        include_custom=True,
    )

    assert len(targets) == 1
    assert targets[0].name == "demo-skill"
    assert targets[0].source == "custom"


def test_skill_summarize_cli_requires_name_or_all():
    runner = CliRunner()
    result = runner.invoke(skill_commands.skill, ["summarize"])

    assert result.exit_code != 0
    assert "Provide a skill name or use --all" in result.output
