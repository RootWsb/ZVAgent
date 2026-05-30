"""
Skill manager for managing skill lifecycle and operations.
"""

import os
import json
import re
from typing import Dict, List, Optional
from pathlib import Path
from common.log import logger
from agent.skills.types import Skill, SkillEntry, SkillSnapshot
from agent.skills.loader import SkillLoader
from agent.skills.formatter import (
    format_skill_entries_for_prompt,
    format_skill_summaries_for_prompt,
)
from agent.skills.summary import (
    SkillSummaryArtifact,
    compute_skill_source_hash,
    read_skill_summary,
    validate_skill_summary,
)

SKILLS_CONFIG_FILE = "skills_config.json"


class SkillManager:
    """Manages skills for an agent."""

    def __init__(
        self,
        builtin_dir: Optional[str] = None,
        custom_dir: Optional[str] = None,
        config: Optional[Dict] = None,
    ):
        """
        Initialize the skill manager.

        :param builtin_dir: Built-in skills directory (project root ``skills/``)
        :param custom_dir: Custom skills directory (workspace ``skills/``)
        :param config: Configuration dictionary
        """
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.builtin_dir = builtin_dir or os.path.join(project_root, 'skills')
        self.custom_dir = custom_dir or os.path.join(project_root, 'workspace', 'skills')
        self.config = config or {}
        self._skills_config_path = os.path.join(self.custom_dir, SKILLS_CONFIG_FILE)

        # skills_config: full skill metadata keyed by name
        # { "web-fetch": {"name": ..., "description": ..., "source": ..., "enabled": true}, ... }
        self.skills_config: Dict[str, dict] = {}

        self.loader = SkillLoader()
        self.skills: Dict[str, SkillEntry] = {}
        self._summary_cache: Dict[str, tuple] = {}
        self._runtime_skill_router = None

        # Load skills on initialization
        self.refresh_skills()

    def refresh_skills(self):
        """Reload all skills from builtin and custom directories, then sync config."""
        self.skills = self.loader.load_all_skills(
            builtin_dir=self.builtin_dir,
            custom_dir=self.custom_dir,
        )
        self._summary_cache = {}
        self._sync_skills_config()
        logger.debug(f"SkillManager: Loaded {len(self.skills)} skills")

    # ------------------------------------------------------------------
    # skills_config.json management
    # ------------------------------------------------------------------
    def _load_skills_config(self) -> Dict[str, dict]:
        """Load skills_config.json from custom_dir. Returns empty dict if not found."""
        if not os.path.exists(self._skills_config_path):
            return {}
        try:
            with open(self._skills_config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception as e:
            logger.warning(f"[SkillManager] Failed to load {SKILLS_CONFIG_FILE}: {e}")
        return {}

    def _save_skills_config(self):
        """Persist skills_config to custom_dir/skills_config.json."""
        os.makedirs(self.custom_dir, exist_ok=True)
        try:
            with open(self._skills_config_path, "w", encoding="utf-8") as f:
                json.dump(self.skills_config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[SkillManager] Failed to save {SKILLS_CONFIG_FILE}: {e}")

    def _sync_skills_config(self):
        """
        Merge directory-scanned skills with the persisted config file.

        - New skills: use metadata.default_enabled as initial enabled state.
        - Existing skills: preserve their persisted enabled state.
        - Skills that no longer exist on disk are removed.
        - name/description/source are always refreshed from the latest scan.
        """
        saved = self._load_skills_config()
        merged: Dict[str, dict] = {}

        for name, entry in self.skills.items():
            skill = entry.skill
            prev = saved.get(name, {})
            category = prev.get("category", "skill")

            if name in saved:
                enabled = prev.get("enabled", True)
            else:
                enabled = entry.metadata.default_enabled if entry.metadata else True

            entry_dict = {
                "name": name,
                "description": skill.description,
                "source": prev.get("source") or skill.source,
                "enabled": enabled,
                "category": category,
            }
            display_name = prev.get("display_name")
            if display_name:
                entry_dict["display_name"] = display_name
            merged[name] = entry_dict

        self.skills_config = merged
        self._save_skills_config()

    def is_skill_enabled(self, name: str) -> bool:
        """
        Check if a skill is enabled according to skills_config.

        :param name: skill name
        :return: True if enabled (default True if not in config)
        """
        entry = self.skills_config.get(name)
        if entry is None:
            return True
        return entry.get("enabled", True)

    def set_skill_enabled(self, name: str, enabled: bool):
        """
        Set a skill's enabled state and persist.

        :param name: skill name
        :param enabled: True to enable, False to disable
        """
        if name not in self.skills_config:
            raise ValueError(f"skill '{name}' not found in config")
        self.skills_config[name]["enabled"] = enabled
        self._save_skills_config()

    def get_skills_config(self) -> Dict[str, dict]:
        """
        Return the full skills_config dict (for query API).

        :return: copy of skills_config
        """
        return dict(self.skills_config)
    
    def get_skill(self, name: str) -> Optional[SkillEntry]:
        """
        Get a skill by name.
        
        :param name: Skill name
        :return: SkillEntry or None if not found
        """
        return self.skills.get(name)
    
    def list_skills(self) -> List[SkillEntry]:
        """
        Get all loaded skills.
        
        :return: List of all skill entries
        """
        return list(self.skills.values())
    
    @staticmethod
    def _normalize_skill_filter(skill_filter: Optional[List[str]]) -> Optional[List[str]]:
        """Normalize a skill_filter list into a flat list of stripped names."""
        if skill_filter is None:
            return None
        normalized = []
        for item in skill_filter:
            if isinstance(item, str):
                name = item.strip()
                if name:
                    normalized.append(name)
            elif isinstance(item, list):
                for subitem in item:
                    if isinstance(subitem, str):
                        name = subitem.strip()
                        if name:
                            normalized.append(name)
        return normalized or None

    def filter_skills(
        self,
        skill_filter: Optional[List[str]] = None,
        include_disabled: bool = False,
    ) -> List[SkillEntry]:
        """
        Filter skills that are eligible (enabled + requirements met).

        :param skill_filter: List of skill names to include (None = all)
        :param include_disabled: Whether to include disabled skills
        :return: Filtered list of eligible skill entries
        """
        from agent.skills.config import should_include_skill

        entries = list(self.skills.values())

        entries = [e for e in entries if should_include_skill(e, self.config)]

        normalized = self._normalize_skill_filter(skill_filter)
        if normalized is not None:
            entries = [e for e in entries if e.skill.name in normalized]

        if not include_disabled:
            entries = [e for e in entries if self.is_skill_enabled(e.skill.name)]

        from config import conf
        if not conf().get("knowledge", True):
            entries = [e for e in entries if e.skill.name != "knowledge-wiki"]

        return entries

    def filter_unavailable_skills(
        self,
        skill_filter: Optional[List[str]] = None,
    ) -> tuple:
        """
        Find skills that are enabled but have unmet requirements.

        :param skill_filter: Optional list of skill names to include
        :return: Tuple of (entries, missing_map) where missing_map maps
                 skill name to its missing requirements dict
        """
        from agent.skills.config import should_include_skill, get_missing_requirements

        entries = list(self.skills.values())

        # Only enabled skills
        entries = [e for e in entries if self.is_skill_enabled(e.skill.name)]

        normalized = self._normalize_skill_filter(skill_filter)
        if normalized is not None:
            entries = [e for e in entries if e.skill.name in normalized]

        # Keep only those that fail should_include_skill (requirements not met)
        unavailable = []
        missing_map: Dict[str, dict] = {}
        for e in entries:
            if not should_include_skill(e, self.config):
                missing = get_missing_requirements(e)
                if missing:
                    unavailable.append(e)
                    missing_map[e.skill.name] = missing

        return unavailable, missing_map

    @staticmethod
    def _config_list(key: str, default: List[str]) -> List[str]:
        try:
            from config import conf
            value = conf().get(key, default)
        except Exception:
            value = default
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, (list, tuple, set)):
            return [str(item).strip() for item in value if str(item).strip()]
        return list(default)

    @staticmethod
    def _config_int(key: str, default: int) -> int:
        try:
            from config import conf
            value = conf().get(key, default)
            return max(0, int(value))
        except Exception:
            return default

    @staticmethod
    def _config_bool(key: str, default: bool) -> bool:
        try:
            from config import conf
            value = conf().get(key, default)
        except Exception:
            value = default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes", "on")
        return bool(value)

    @staticmethod
    def _config_value(key: str, default=None):
        try:
            from config import conf
            return conf().get(key, default)
        except Exception:
            return default

    @staticmethod
    def _normalize_text(text: str) -> str:
        return re.sub(r"\s+", " ", str(text or "").lower()).strip()

    @staticmethod
    def _skill_summary_path(entry: SkillEntry) -> str:
        skill_path = Path(entry.skill.file_path)
        if skill_path.name.lower() == "skill.md":
            return str(skill_path.with_name("SKILL.summary.json"))
        return str(skill_path.with_suffix(".summary.json"))

    def get_skill_summary(self, name: str) -> Optional[SkillSummaryArtifact]:
        """Load a validated summary sidecar for one skill when available."""
        entry = self.get_skill(name)
        if not entry:
            return None

        summary_path = self._skill_summary_path(entry)
        if not os.path.exists(summary_path):
            return None

        current_hash = compute_skill_source_hash(entry.skill.content)
        try:
            summary_mtime = os.path.getmtime(summary_path)
        except OSError:
            return None

        cache_key = entry.skill.name
        cached = self._summary_cache.get(cache_key)
        if cached and cached[0] == current_hash and cached[1] == summary_mtime:
            return cached[2]

        artifact: Optional[SkillSummaryArtifact] = None
        try:
            artifact = read_skill_summary(summary_path)
            validation = validate_skill_summary(
                artifact,
                skill_content=entry.skill.content,
                skill_name=entry.skill.name,
                source_hash=current_hash,
            )
            if not validation.ok:
                logger.warning(
                    f"[SkillManager] Invalid summary for skill '{entry.skill.name}': "
                    f"{'; '.join(validation.errors[:3])}"
                )
                artifact = None
        except Exception as e:
            logger.warning(
                f"[SkillManager] Failed to read summary for skill '{entry.skill.name}': {e}"
            )
            artifact = None

        self._summary_cache[cache_key] = (current_hash, summary_mtime, artifact)
        return artifact

    def get_candidate_skill_summaries(
        self,
        skill_filter: Optional[List[str]] = None,
        max_candidates: Optional[int] = None,
    ) -> List[SkillSummaryArtifact]:
        """Return valid Level 2 summaries for the routed candidate skills."""
        if not self._config_bool("skill_summary_enabled", True):
            return []

        normalized = self._normalize_skill_filter(skill_filter)
        if not normalized:
            return []

        if max_candidates is None:
            max_candidates = self._config_int("skill_summary_max_candidates", 3)
        max_candidates = max(0, int(max_candidates or 0))
        if max_candidates <= 0:
            return []

        summaries: List[SkillSummaryArtifact] = []
        for name in normalized[:max_candidates]:
            artifact = self.get_skill_summary(name)
            if artifact:
                summaries.append(artifact)
        return summaries

    def build_skill_summaries_prompt(
        self,
        skill_filter: Optional[List[str]] = None,
        max_candidates: Optional[int] = None,
    ) -> str:
        """Build a prompt block for Level 2 candidate skill summaries."""
        summaries = self.get_candidate_skill_summaries(
            skill_filter=skill_filter,
            max_candidates=max_candidates,
        )
        return format_skill_summaries_for_prompt(summaries)

    def _always_include_skill_names(self) -> List[str]:
        configured = self._config_list(
            "skill_prompt_always_include",
            ["task-budget-router", "source-registry", "quality-guardrails"],
        )
        always = []
        for entry in self.skills.values():
            if entry.metadata and entry.metadata.always:
                always.append(entry.skill.name)
        return list(dict.fromkeys(configured + always))

    def _limit_prompt_entries(
        self,
        entries: List[SkillEntry],
        skill_filter: Optional[List[str]] = None,
        max_skills_key: str = "skill_prompt_max_skills",
    ) -> tuple:
        """Return entries selected for the system prompt and the omitted count."""
        if skill_filter is not None:
            return entries, 0

        max_skills = self._config_int(max_skills_key, 8)
        if max_skills <= 0 or len(entries) <= max_skills:
            return entries, 0

        always_names = set(self._always_include_skill_names())
        selected = [e for e in entries if e.skill.name in always_names]
        selected_names = {e.skill.name for e in selected}

        for entry in entries:
            if len(selected) >= max_skills:
                break
            if entry.skill.name in selected_names:
                continue
            selected.append(entry)
            selected_names.add(entry.skill.name)

        omitted = max(0, len(entries) - len(selected))
        return selected, omitted

    def _progressive_level1_entries(self, entries: List[SkillEntry]) -> tuple:
        """Return the lightweight Level 1 catalog entries."""
        return self._limit_prompt_entries(
            entries,
            skill_filter=None,
            max_skills_key="skill_level1_max_skills",
        )

    def _select_relevant_skills_ml(
        self,
        query: str,
        entries: List[SkillEntry],
        max_skills: int,
    ) -> Optional[List[str]]:
        """Use trained ML router when enabled; return None to fallback."""
        if not self._config_bool("skill_router_enabled", False):
            return None

        try:
            from agent.skills.skill_router import RuntimeSkillRouter

            if self._runtime_skill_router is None:
                model_path = self._config_value(
                    "skill_router_model_path",
                    "training/skill_router/checkpoints/skill_router/best",
                )
                skill_index_path = self._config_value(
                    "skill_router_skill_index_path",
                    "training/skill_router/checkpoints/skill_router/skill_index.json",
                )
                threshold = float(self._config_value("skill_router_threshold", 0.3))
                device = self._config_value("skill_router_device", None)
                self._runtime_skill_router = RuntimeSkillRouter(
                    model_path=model_path,
                    skill_index_path=skill_index_path,
                    device=device,
                    threshold=threshold,
                )

            top_k = self._config_int("skill_router_top_k", max_skills)
            top_k = max(1, min(int(top_k or max_skills), max_skills))
            available_skills = [entry.skill.name for entry in entries]
            selected = self._runtime_skill_router.predict(
                query,
                top_k=top_k,
                available_skills=available_skills,
            )
            always_names = [
                name for name in self._always_include_skill_names()
                if name in available_skills and name not in selected
            ]
            selected = (always_names + selected)[:max_skills]
            if selected:
                logger.debug(f"[SkillManager] ML router selected: {selected}")
                return selected
        except Exception as e:
            logger.warning(f"[SkillManager] ML router failed, fallback to legacy: {e}")

        return None

    def select_relevant_skills(
        self,
        query: str,
        max_skills: Optional[int] = None,
    ) -> List[str]:
        """
        Pick a compact set of skills for one user request.

        This keeps the system prompt small as the skill library grows, while
        still including core routing/quality skills and any skill explicitly
        mentioned by name.
        """
        entries = self.filter_skills(skill_filter=None, include_disabled=False)
        if not entries:
            return []

        if max_skills is None:
            max_skills = self._config_int("skill_prompt_max_skills", 8)
        max_skills = max(1, int(max_skills or 8))

        ml_selected = self._select_relevant_skills_ml(query, entries, max_skills)
        if ml_selected is not None:
            return ml_selected

        text = self._normalize_text(query)
        always_names = set(self._always_include_skill_names())
        scores: Dict[str, int] = {}

        domain_keywords = {
            "paper-download": ["download", "save", "fetch", "pdf", "paper", "doi", "arxiv", "pmc", "下载", "保存", "论文", "全文"],
            "ai-tech-digest": ["ai", "openai", "gpt", "claude", "gemini", "deepseek", "模型", "大模型", "人工智能"],
            "brief-automation": ["日报", "周报", "月报", "简报", "定时", "汇总", "自动归档"],
            "citation-management": ["引用", "参考文献", "citation", "bibliography", "doi"],
            "crypto-news": ["bitcoin", "btc", "ethereum", "eth", "defi", "crypto", "加密", "币", "链上"],
            "economic-analysis": ["经济", "cpi", "gdp", "通胀", "利率", "央行", "汇率", "美联储", "就业"],
            "feedback-template-evolver": ["反馈", "模板", "改进", "优化回答", "进化"],
            "huggingface-datasets": ["dataset", "datasets", "数据集", "huggingface"],
            "huggingface-papers": ["paper", "论文", "arxiv", "huggingface"],
            "image-generation": ["图片", "图像", "画", "生成图", "image"],
            "knowledge-compression-indexer": ["知识库", "压缩", "索引", "上下文", "token"],
            "knowledge-wiki": ["知识沉淀", "知识库", "归档", "记录", "wiki"],
            "literature-review": ["文献综述", "综述", "literature", "review"],
            "paper-lookup": ["查论文", "论文", "paper", "doi", "arxiv"],
            "research-assistant": ["研究", "调研", "报告", "分析报告", "深度", "资料"],
            "source-registry": ["来源", "信源", "检索", "搜索", "最新", "新闻", "网页", "验证"],
            "statistical-analysis": ["统计", "回归", "显著性", "数据分析", "statistical"],
            "surf": ["网页", "浏览", "网站", "抓取", "browser", "surf"],
            "apify-ultimate-scraper": ["爬虫", "抓取", "scraper", "apify", "采集"],
            "task-budget-router": ["复杂", "深度", "快速", "预算", "token", "规划"],
            "usage-learning-optimizer": ["偏好", "记住", "以后", "习惯", "学习我的"],
            "usfiscaldata": ["美国财政", "treasury", "fiscal", "债务", "赤字"],
            "vertical-research-orchestrator": ["跨领域", "复杂问题", "规划", "研究方案", "报告"],
        }

        for entry in entries:
            name = entry.skill.name
            haystack = self._normalize_text(
                f"{name} {name.replace('-', ' ')} {entry.skill.description}"
            )
            score = 0
            if name in always_names:
                score += 100
            if name in text or name.replace("-", " ") in text:
                score += 80
            for keyword in domain_keywords.get(name, []):
                if keyword.lower() in text:
                    score += 20
            for token in re.findall(r"[a-zA-Z0-9_\-]{3,}", text):
                if token in haystack:
                    score += 3
            if score > 0:
                scores[name] = score

        if not scores:
            for name in always_names:
                if any(e.skill.name == name for e in entries):
                    scores[name] = 100

        ranked = sorted(
            entries,
            key=lambda e: (-scores.get(e.skill.name, 0), e.skill.name),
        )
        selected = [e.skill.name for e in ranked if scores.get(e.skill.name, 0) > 0]
        if not selected:
            selected = [e.skill.name for e in entries[:max_skills]]

        return selected[:max_skills]

    def build_skills_prompt(
        self,
        skill_filter: Optional[List[str]] = None,
    ) -> str:
        """
        Build a formatted prompt containing available skills
        and brief hints for unavailable ones.

        :param skill_filter: Optional list of skill names to include
        :return: Formatted skills prompt
        """
        from common.log import logger
        from agent.skills.formatter import format_unavailable_skills_for_prompt

        progressive_enabled = self._config_bool("skill_progressive_loading_enabled", True)
        if progressive_enabled:
            eligible = self.filter_skills(skill_filter=None, include_disabled=False)
            selected, omitted_count = self._progressive_level1_entries(eligible)
            routed_filter = self._normalize_skill_filter(skill_filter)
        else:
            eligible = self.filter_skills(skill_filter=skill_filter, include_disabled=False)
            selected, omitted_count = self._limit_prompt_entries(
                eligible,
                skill_filter=skill_filter,
            )
            routed_filter = skill_filter

        logger.debug(
            f"[SkillManager] Eligible: {len(eligible)} skills (total: {len(self.skills)}), "
            f"selected Level 1: {len(selected)}"
        )
        if selected:
            skill_names = [e.skill.name for e in selected]
            logger.debug(f"[SkillManager] Level 1 skills: {skill_names}")

        max_desc_chars = self._config_int("skill_prompt_description_chars", 180)
        result = format_skill_entries_for_prompt(
            selected,
            max_description_chars=max_desc_chars,
        )

        if omitted_count:
            result += (
                f"\n\n<!-- {omitted_count} enabled skills were omitted from this "
                "prompt to keep responses fast. Use explicit skill filters for "
                "targeted runs. -->"
            )

        include_unavailable = bool(self._config_int("skill_prompt_include_unavailable", 0))
        unavailable, missing_map = self.filter_unavailable_skills(skill_filter=skill_filter)
        if include_unavailable and unavailable:
            unavailable_names = [e.skill.name for e in unavailable]
            logger.debug(f"[SkillManager] Unavailable skills (setup needed): {unavailable_names}")
            result += format_unavailable_skills_for_prompt(unavailable, missing_map)

        summary_prompt = self.build_skill_summaries_prompt(skill_filter=routed_filter)
        if summary_prompt:
            result += summary_prompt

        logger.debug(f"[SkillManager] Generated prompt length: {len(result)}")
        return result
    
    def build_skill_snapshot(
        self,
        skill_filter: Optional[List[str]] = None,
        version: Optional[int] = None,
    ) -> SkillSnapshot:
        """
        Build a snapshot of skills for a specific run.
        
        :param skill_filter: Optional list of skill names to include
        :param version: Optional version number for the snapshot
        :return: SkillSnapshot
        """
        entries = self.filter_skills(skill_filter=skill_filter, include_disabled=False)
        prompt = format_skill_entries_for_prompt(entries)
        
        skills_info = []
        resolved_skills = []
        
        for entry in entries:
            skills_info.append({
                'name': entry.skill.name,
                'primary_env': entry.metadata.primary_env if entry.metadata else None,
            })
            resolved_skills.append(entry.skill)
        
        return SkillSnapshot(
            prompt=prompt,
            skills=skills_info,
            resolved_skills=resolved_skills,
            version=version,
        )
    
    def sync_skills_to_workspace(self, target_workspace_dir: str):
        """
        Sync all loaded skills to a target workspace directory.
        
        This is useful for sandbox environments where skills need to be copied.
        
        :param target_workspace_dir: Target workspace directory
        """
        import shutil
        
        target_skills_dir = os.path.join(target_workspace_dir, 'skills')
        
        # Remove existing skills directory
        if os.path.exists(target_skills_dir):
            shutil.rmtree(target_skills_dir)
        
        # Create new skills directory
        os.makedirs(target_skills_dir, exist_ok=True)
        
        # Copy each skill
        for entry in self.skills.values():
            skill_name = entry.skill.name
            source_dir = entry.skill.base_dir
            target_dir = os.path.join(target_skills_dir, skill_name)
            
            try:
                shutil.copytree(source_dir, target_dir)
                logger.debug(f"Synced skill '{skill_name}' to {target_dir}")
            except Exception as e:
                logger.warning(f"Failed to sync skill '{skill_name}': {e}")
        
        logger.info(f"Synced {len(self.skills)} skills to {target_skills_dir}")
    
    def get_skill_by_key(self, skill_key: str) -> Optional[SkillEntry]:
        """
        Get a skill by its skill key (which may differ from name).
        
        :param skill_key: Skill key to look up
        :return: SkillEntry or None
        """
        for entry in self.skills.values():
            if entry.metadata and entry.metadata.skill_key == skill_key:
                return entry
            if entry.skill.name == skill_key:
                return entry
        return None
