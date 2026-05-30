"""
Skill formatter for generating prompts from skills.
"""

from typing import Dict, List, Optional
from agent.skills.types import Skill, SkillEntry
from agent.skills.summary import SkillSummaryArtifact


def format_skills_for_prompt(skills: List[Skill], max_description_chars: Optional[int] = None) -> str:
    """
    Format skills for inclusion in a system prompt.
    
    Uses XML format per Agent Skills standard.
    Skills with disable_model_invocation=True are excluded.
    
    :param skills: List of skills to format
    :return: Formatted prompt text
    """
    # Filter out skills that should not be invoked by the model
    visible_skills = [s for s in skills if not s.disable_model_invocation]
    
    if not visible_skills:
        return ""
    
    lines = [
        "",
        "<available_skills>",
        "  <loading_policy>",
        "    Level 1: this catalog is for broad routing only.",
        "    Level 2: candidate_skill_summaries are for triage only.",
        "    Level 3: before executing a skill workflow, read the full SKILL.md from location.",
        "  </loading_policy>",
    ]

    for skill in visible_skills:
        lines.append("  <skill>")
        lines.append(f"    <name>{_escape_xml(skill.name)}</name>")
        description = _truncate_text(skill.description, max_description_chars)
        lines.append(f"    <description>{_escape_xml(description)}</description>")
        lines.append(f"    <location>{_escape_xml(skill.file_path)}</location>")
        lines.append(f"    <base_dir>{_escape_xml(skill.base_dir)}</base_dir>")
        lines.append("  </skill>")
    
    lines.append("</available_skills>")
    
    return "\n".join(lines)


def format_skill_entries_for_prompt(
    entries: List[SkillEntry],
    max_description_chars: Optional[int] = None,
) -> str:
    """
    Format skill entries for inclusion in a system prompt.
    
    :param entries: List of skill entries to format
    :return: Formatted prompt text
    """
    skills = [entry.skill for entry in entries]
    return format_skills_for_prompt(skills, max_description_chars=max_description_chars)


def format_skill_summaries_for_prompt(
    summaries: List[SkillSummaryArtifact],
) -> str:
    """Format Level 2 candidate summaries for the system prompt."""
    if not summaries:
        return ""

    lines = [
        "",
        "<candidate_skill_summaries>",
    ]

    for artifact in summaries:
        level_1 = artifact.level_1
        level_2 = artifact.level_2
        lines.append("  <skill_summary>")
        lines.append(f"    <name>{_escape_xml(level_1.name)}</name>")
        lines.append(f"    <one_line>{_escape_xml(level_2.one_line)}</one_line>")
        if level_1.tags:
            lines.append(f"    <tags>{_escape_xml(', '.join(level_1.tags))}</tags>")
        _append_list_block(lines, "use_when", level_2.use_when)
        _append_list_block(lines, "avoid_when", level_2.avoid_when)
        _append_list_block(lines, "prerequisites", level_2.prerequisites)
        _append_list_block(lines, "key_inputs", level_2.key_inputs)
        _append_list_block(lines, "workflow_outline", level_2.workflow_outline)
        _append_list_block(lines, "tool_dependencies", level_2.tool_dependencies)
        _append_list_block(lines, "risk_flags", level_2.risk_flags)
        lines.append("  </skill_summary>")

    lines.append("</candidate_skill_summaries>")
    return "\n".join(lines)


def format_unavailable_skills_for_prompt(
    entries: List[SkillEntry],
    missing_map: Dict[str, Dict[str, List[str]]],
) -> str:
    """
    Format unavailable (requires-not-met) skills as brief setup hints
    so the AI can guide users to configure them.

    :param entries: List of unavailable skill entries
    :param missing_map: Dict mapping skill name to its missing requirements
    :return: Formatted prompt text
    """
    if not entries:
        return ""

    lines = [
        "",
        "<unavailable_skills>",
        "The following skills are installed but not yet ready. "
        "Guide the user to complete the setup when relevant.",
    ]

    for entry in entries:
        skill = entry.skill
        missing = missing_map.get(skill.name, {})

        missing_parts = []
        for key, values in missing.items():
            missing_parts.append(f"{key}: {', '.join(values)}")
        missing_str = "; ".join(missing_parts) if missing_parts else "unknown"

        setup_hint = _extract_setup_hint(skill)

        lines.append("  <skill>")
        lines.append(f"    <name>{_escape_xml(skill.name)}</name>")
        lines.append(f"    <description>{_escape_xml(skill.description)}</description>")
        lines.append(f"    <missing>{_escape_xml(missing_str)}</missing>")
        if setup_hint:
            lines.append(f"    <setup>{_escape_xml(setup_hint)}</setup>")
        lines.append("  </skill>")

    lines.append("</unavailable_skills>")
    return "\n".join(lines)


def _extract_setup_hint(skill: Skill) -> str:
    """
    Extract the Setup section from SKILL.md content as a brief hint.
    Returns the first few lines of the ## Setup section.
    """
    content = skill.content
    if not content:
        return ""

    import re
    match = re.search(r'^##\s+Setup\s*\n(.*?)(?=\n##\s|\Z)', content, re.MULTILINE | re.DOTALL)
    if not match:
        return ""

    setup_text = match.group(1).strip()
    lines = setup_text.split('\n')
    hint_lines = [l.strip() for l in lines[:6] if l.strip()]
    return ' '.join(hint_lines)[:300]


def _escape_xml(text: str) -> str:
    """Escape XML special characters."""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))


def _truncate_text(text: str, max_chars: Optional[int]) -> str:
    """Keep skill descriptions compact in the system prompt."""
    if not text or not max_chars or max_chars <= 0:
        return text or ""
    clean = " ".join(str(text).split())
    if len(clean) <= max_chars:
        return clean
    return clean[:max_chars].rstrip() + "..."


def _append_list_block(lines: List[str], tag: str, values: List[str]):
    if not values:
        return
    lines.append(f"    <{tag}>")
    for value in values:
        lines.append(f"      <item>{_escape_xml(str(value))}</item>")
    lines.append(f"    </{tag}>")
