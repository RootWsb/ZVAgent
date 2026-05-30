"""
Skills module for agent system.

This module provides the framework for loading, managing, and executing skills.
Skills are markdown files with frontmatter that provide specialized instructions
for specific tasks.
"""

from agent.skills.types import (
    Skill,
    SkillEntry,
    SkillMetadata,
    SkillInstallSpec,
    LoadSkillsResult,
)
from agent.skills.loader import SkillLoader
from agent.skills.manager import SkillManager
from agent.skills.service import SkillService
from agent.skills.formatter import format_skills_for_prompt
from agent.skills.summary import (
    SUMMARY_SCHEMA_VERSION,
    SkillLevel1Card,
    SkillLevel2Card,
    SkillSummaryArtifact,
    SkillSummaryGenerator,
    SkillSummaryValidationResult,
    compute_skill_source_hash,
    read_skill_summary,
    validate_skill_summary,
    write_skill_summary,
)
from agent.skills.summary_generator import (
    SUMMARY_GENERATOR_PROMPT_VERSION,
    SkillSummaryGenerationError,
    SkillSummaryGenerationResult,
    generate_skill_summary,
    get_skill_summary_path,
)

__all__ = [
    "Skill",
    "SkillEntry",
    "SkillMetadata",
    "SkillInstallSpec",
    "LoadSkillsResult",
    "SkillLoader",
    "SkillManager",
    "SkillService",
    "format_skills_for_prompt",
    "SUMMARY_SCHEMA_VERSION",
    "SkillLevel1Card",
    "SkillLevel2Card",
    "SkillSummaryArtifact",
    "SkillSummaryGenerator",
    "SkillSummaryValidationResult",
    "compute_skill_source_hash",
    "read_skill_summary",
    "validate_skill_summary",
    "write_skill_summary",
    "SUMMARY_GENERATOR_PROMPT_VERSION",
    "SkillSummaryGenerationError",
    "SkillSummaryGenerationResult",
    "generate_skill_summary",
    "get_skill_summary_path",
]
