from agent.skills.summary import (
    SUMMARY_SCHEMA_VERSION,
    SkillLevel1Card,
    SkillLevel2Card,
    SkillSummaryArtifact,
    SkillSummaryGenerator,
    compute_skill_source_hash,
    validate_skill_summary,
    write_skill_summary,
)
from agent.skills.manager import SkillManager
from config import config as global_config


def _build_artifact(skill_content: str) -> SkillSummaryArtifact:
    return SkillSummaryArtifact(
        schema_version=SUMMARY_SCHEMA_VERSION,
        skill_name="demo-skill",
        source_path="skills/demo-skill/SKILL.md",
        source_hash=compute_skill_source_hash(skill_content),
        generated_at="2026-05-21T10:00:00Z",
        generator=SkillSummaryGenerator(
            provider="openai",
            model="gpt-5.2",
            prompt_version="skill-summary-v1",
        ),
        level_1=SkillLevel1Card(
            name="demo-skill",
            description="Summarize a demo workflow.",
            tags=["demo", "workflow"],
        ),
        level_2=SkillLevel2Card(
            one_line="Use this skill for demo workflow requests.",
            use_when=["The task is a demo workflow request."],
            prerequisites=["Use read before running scripts."],
            workflow_outline=["read the skill", "inspect scripts", "run the workflow"],
            tool_dependencies=["read", "bash"],
            risk_flags=["Do not skip the validation step."],
        ),
        evidence={
            "use_when": ["Use this skill for demo workflow requests."],
            "prerequisites": ["Use read before running scripts."],
            "workflow_outline": ["Read the skill, inspect scripts, then run the workflow."],
            "tool_dependencies": ["Use tools: read and bash."],
            "risk_flags": ["Do not skip the validation step."],
        },
    )


def test_validate_skill_summary_accepts_grounded_artifact():
    skill_content = """
    # Demo Skill

    Use this skill for demo workflow requests.
    Use read before running scripts.
    Read the skill, inspect scripts, then run the workflow.
    Use tools: read and bash.
    Do not skip the validation step.
    """
    artifact = _build_artifact(skill_content)

    result = validate_skill_summary(
        artifact,
        skill_content=skill_content,
        skill_name="demo-skill",
        source_hash=compute_skill_source_hash(skill_content),
    )

    assert result.ok
    assert not result.errors


def test_validate_skill_summary_rejects_hash_mismatch():
    skill_content = "Use this skill for demo workflow requests."
    artifact = _build_artifact(skill_content)

    result = validate_skill_summary(
        artifact,
        skill_content=skill_content,
        source_hash=compute_skill_source_hash("different content"),
    )

    assert not result.ok
    assert any("source_hash" in error for error in result.errors)


def test_validate_skill_summary_rejects_ungrounded_evidence():
    skill_content = "Use this skill for demo workflow requests."
    artifact = _build_artifact(skill_content)
    artifact.evidence["risk_flags"] = ["This sentence does not exist in the source."]

    result = validate_skill_summary(
        artifact,
        skill_content=skill_content,
    )

    assert not result.ok
    assert any("evidence.risk_flags" in error for error in result.errors)


def test_skill_manager_builds_candidate_summary_prompt(tmp_path, monkeypatch):
    skill_dir = tmp_path / "skills" / "demo-skill"
    skill_dir.mkdir(parents=True)
    skill_content = """---
name: demo-skill
description: Demo workflow skill.
---

Use this skill for demo workflow requests.
Use read before running scripts.
Read the skill, inspect scripts, then run the workflow.
Use tools: read and bash.
Do not skip the validation step.
"""
    (skill_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")

    artifact = _build_artifact(skill_content)
    artifact.source_path = str(skill_dir / "SKILL.md")
    write_skill_summary(str(skill_dir / "SKILL.summary.json"), artifact)

    monkeypatch.setitem(global_config, "skill_summary_enabled", True)
    monkeypatch.setitem(global_config, "skill_summary_max_candidates", 3)

    manager = SkillManager(
        builtin_dir=str(tmp_path / "skills"),
        custom_dir=str(tmp_path / "workspace-skills"),
    )
    prompt = manager.build_skills_prompt(skill_filter=["demo-skill"])

    assert "<available_skills>" in prompt
    assert "<candidate_skill_summaries>" in prompt
    assert "<name>demo-skill</name>" in prompt
    assert "Use this skill for demo workflow requests." in prompt


def test_progressive_loading_keeps_full_level1_catalog_with_candidate_level2(tmp_path, monkeypatch):
    root = tmp_path / "skills"
    demo_dir = root / "demo-skill"
    other_dir = root / "other-skill"
    demo_dir.mkdir(parents=True)
    other_dir.mkdir(parents=True)

    demo_content = """---
name: demo-skill
description: Demo workflow skill.
---

Use this skill for demo workflow requests.
Use read before running scripts.
Read the skill, inspect scripts, then run the workflow.
Use tools: read and bash.
Do not skip the validation step.
"""
    other_content = """---
name: other-skill
description: Other workflow skill.
---

Use this skill for unrelated workflow requests.
"""
    (demo_dir / "SKILL.md").write_text(demo_content, encoding="utf-8")
    (other_dir / "SKILL.md").write_text(other_content, encoding="utf-8")

    artifact = _build_artifact(demo_content)
    artifact.source_path = str(demo_dir / "SKILL.md")
    write_skill_summary(str(demo_dir / "SKILL.summary.json"), artifact)

    monkeypatch.setitem(global_config, "skill_progressive_loading_enabled", True)
    monkeypatch.setitem(global_config, "skill_level1_max_skills", 0)
    monkeypatch.setitem(global_config, "skill_summary_enabled", True)
    monkeypatch.setitem(global_config, "skill_summary_max_candidates", 3)

    manager = SkillManager(
        builtin_dir=str(root),
        custom_dir=str(tmp_path / "workspace-skills"),
    )
    prompt = manager.build_skills_prompt(skill_filter=["demo-skill"])

    assert "<available_skills>" in prompt
    assert "<loading_policy>" in prompt
    assert "<name>demo-skill</name>" in prompt
    assert "<name>other-skill</name>" in prompt
    assert "<candidate_skill_summaries>" in prompt
    assert "Use this skill for demo workflow requests." in prompt
    assert "Use this skill for unrelated workflow requests." not in prompt
