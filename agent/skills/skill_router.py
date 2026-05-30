"""
Runtime loader for the trained SkillRouter classifier.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from common.log import logger


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class RuntimeSkillRouter:
    """Lazy wrapper around training.skill_router.model.SkillRouter."""

    def __init__(
        self,
        model_path: str,
        skill_index_path: Optional[str] = None,
        device: Optional[str] = None,
        threshold: float = 0.3,
    ):
        self.model_path = self._resolve_path(model_path)
        if skill_index_path:
            self.skill_index_path = self._resolve_path(skill_index_path)
        else:
            candidate = self.model_path.parent / "skill_index.json"
            if not candidate.exists():
                candidate = self.model_path.parent.parent / "skill_index.json"
            self.skill_index_path = candidate
        self.device = device
        self.threshold = threshold
        self._model = None
        self._skill_names: List[str] = []

    @staticmethod
    def _resolve_path(path: str) -> Path:
        path_obj = Path(path)
        if path_obj.is_absolute():
            return path_obj
        return PROJECT_ROOT / path_obj

    def _load_skill_names(self) -> List[str]:
        with open(self.skill_index_path, "r", encoding="utf-8") as f:
            skill_index: Dict[str, int] = json.load(f)
        names = [None] * len(skill_index)
        for name, index in skill_index.items():
            index = int(index)
            if 0 <= index < len(names):
                names[index] = name
        return [name or f"<missing-{i}>" for i, name in enumerate(names)]

    def _ensure_loaded(self):
        if self._model is not None:
            return

        training_root = PROJECT_ROOT
        if str(training_root) not in sys.path:
            sys.path.insert(0, str(training_root))

        try:
            import torch
            from training.skill_router.model import SkillRouter

            device = self.device
            if device is None:
                device = "cuda" if torch.cuda.is_available() else "cpu"
            self._skill_names = self._load_skill_names()
            self._model = SkillRouter.load_classifier(
                str(self.model_path),
                device=device,
                local_files_only=True,
            )
            logger.info(
                f"[SkillRouter] Loaded ML router from {self.model_path} "
                f"with {len(self._skill_names)} labels on {device}"
            )
        except Exception as e:
            self._model = None
            logger.warning(f"[SkillRouter] Failed to load ML router: {e}")
            raise

    def predict(self, query: str, top_k: int, available_skills: List[str]) -> List[str]:
        self._ensure_loaded()
        results = self._model.predict(
            query,
            self._skill_names,
            top_k=top_k,
            threshold=self.threshold,
        )
        available = set(available_skills)
        selected = []
        seen = set()
        for item in results:
            skill = item.get("skill")
            if skill in available and skill not in seen:
                selected.append(skill)
                seen.add(skill)
        return selected
