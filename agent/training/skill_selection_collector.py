#!/usr/bin/env python3
"""
Skill Selection Collector - 实时收集 skill 路由决策数据

用于在 ZVAgent 运行时记录每次 skill 选择决策，为 SkillRouter 训练提供数据。

用法：
    # 方式 1：集成到 agent_bridge.py（推荐）
    # 在 agent_bridge.py 的 reply_agent() 中调用 record_selection()

    # 方式 2：独立使用
    from agent.training.skill_selection_collector import SkillSelectionCollector
    collector = SkillSelectionCollector()
    collector.record_selection(...)
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
from common.log import logger


class SkillSelectionCollector:
    """
    收集 skill 路由决策数据，用于训练 SkillRouter 分类器。

    数据格式：
    {
        "user_message": "用户输入",
        "selected_skills": ["skill-a", "skill-b"],
        "available_skills": ["skill-a", "skill-b", ..., "skill-n"],
        "tool_events": [...],  # 可选，实际工具调用记录
        "timestamp": 1234567890,
        "session_id": "session_xxx"
    }
    """

    def __init__(self, output_dir: str = None):
        """
        初始化 collector。

        Args:
            output_dir: 数据保存目录（默认: ~/zvagent/training/data）
        """
        if output_dir is None:
            from config import conf
            from common.utils import expand_path
            workspace = expand_path(conf().get("agent_workspace", "runtime/workspace"))
            output_dir = os.path.join(workspace, "training", "data")

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = self.output_dir / "skill_selections.jsonl"

    def record_selection(
        self,
        user_message: str,
        selected_skills: List[str],
        available_skills: List[str],
        tool_events: Optional[List[Dict]] = None,
        session_id: Optional[str] = None,
    ):
        """
        记录一次 skill 选择决策。

        Args:
            user_message: 用户输入消息
            selected_skills: 本次选择的 skill 列表
            available_skills: 可用的全部 skill 列表
            tool_events: 可选，本次运行的工具调用事件
            session_id: 可选，会话 ID
        """
        record = {
            "user_message": user_message,
            "selected_skills": selected_skills,
            "available_skills": available_skills,
            "tool_events": tool_events or [],
            "timestamp": time.time(),
            "session_id": session_id,
        }

        try:
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            logger.debug(
                f"[SkillCollector] Recorded selection: {len(selected_skills)} skills"
            )
        except Exception as e:
            logger.warning(f"[SkillCollector] Failed to record selection: {e}")

    def load_records(self) -> List[Dict]:
        """
        加载所有已收集的记录。

        Returns:
            记录列表
        """
        if not self.output_file.exists():
            return []

        records = []
        with open(self.output_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return records

    def get_stats(self) -> Dict:
        """
        获取收集统计信息。

        Returns:
            统计信息字典
        """
        records = self.load_records()
        if not records:
            return {"total_records": 0}

        skill_counts = {}
        for record in records:
            for skill in record.get("selected_skills", []):
                skill_counts[skill] = skill_counts.get(skill, 0) + 1

        return {
            "total_records": len(records),
            "skill_distribution": skill_counts,
            "avg_skills_per_query": sum(
                len(r.get("selected_skills", [])) for r in records
            ) / len(records),
        }


# 全局 collector 实例
_collector: Optional[SkillSelectionCollector] = None


def get_collector(output_dir: str = None) -> SkillSelectionCollector:
    """获取全局 collector 实例（单例模式）。"""
    global _collector
    if _collector is None:
        _collector = SkillSelectionCollector(output_dir)
    return _collector


def record_selection(
    user_message: str,
    selected_skills: List[str],
    available_skills: List[str],
    tool_events: Optional[List[Dict]] = None,
    session_id: Optional[str] = None,
):
    """
    便捷函数：记录一次 skill 选择决策。

    用于集成到 agent_bridge.py 中：
        from agent.training.skill_selection_collector import record_selection
        record_selection(
            user_message=query,
            selected_skills=skill_filter,
            available_skills=[e.skill.name for e in agent.skill_manager.list_skills()],
        )
    """
    collector = get_collector()
    collector.record_selection(
        user_message=user_message,
        selected_skills=selected_skills,
        available_skills=available_skills,
        tool_events=tool_events,
        session_id=session_id,
    )
