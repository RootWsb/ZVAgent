#!/usr/bin/env python3
"""
Auto Collector - Phase B 自动对话数据收集器

启动 ZVAgent，自动发送 synthetic_data_generator.py 生成的问题，
记录每次的 skill 路由决策和 tool 调用事件。

用法：
    python auto_collector.py --input synthetic_data.jsonl --output real_data.jsonl

前置条件：
    1. 先运行 synthetic_data_generator.py 生成 synthetic_data.jsonl
    2. 确保 ZVAgent 可以正常启动（config.json 已配置）

环境变量：
    DEEPSEEK_API_KEY: DeepSeek API 密钥（如果使用 DeepSeek 模型）

依赖：
    pip install tqdm
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

from tqdm import tqdm

# 添加项目根目录到 path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_synthetic_data(input_path: str) -> List[Dict]:
    """
    加载 synthetic_data_generator.py 生成的数据。

    Args:
        input_path: JSONL 文件路径

    Returns:
        数据列表
    """
    data = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return data


def initialize_agent():
    """
    初始化 ZVAgent 实例。

    Returns:
        Agent 实例
    """
    # config.load_config() reads ./config.json, so this standalone script must
    # run from the ZVagent package root no matter where the user launched it.
    os.chdir(PROJECT_ROOT)

    from config import load_config
    load_config()

    from agent.protocol import Agent
    from agent.tools import ToolManager
    from agent.skills import SkillManager

    # 初始化 tool manager
    tool_manager = ToolManager()
    tools = tool_manager.load_tools()

    # 初始化 skill manager
    skill_manager = SkillManager()

    # 创建 agent（简化版，不依赖 LLM 模型）
    agent = Agent(
        system_prompt="You are a helpful assistant.",
        tools=tools,
        skill_manager=skill_manager,
        enable_skills=True,
    )

    return agent


def collect_single_query(
    agent,
    query: str,
    available_skills: List[str],
) -> Dict:
    """
    发送单个问题，记录 skill 选择决策。

    Args:
        agent: Agent 实例
        query: 用户问题
        available_skills: 可用 skill 列表

    Returns:
        收集的数据记录
    """
    # 记录选择前的状态
    start_time = time.time()

    try:
        # 调用 skill 选择逻辑
        selected_skills = agent.skill_manager.select_relevant_skills(query)

        # 模拟 tool_events（实际部署时可以从 agent 获取真实数据）
        # 这里只记录 skill 选择决策
        tool_events = []

        record = {
            "user_message": query,
            "selected_skills": selected_skills,
            "available_skills": available_skills,
            "tool_events": tool_events,
            "timestamp": time.time(),
            "generation_method": "auto_collect",
            "collection_time_ms": int((time.time() - start_time) * 1000),
        }

        return record

    except Exception as e:
        print(f"  X 收集失败: {query[:50]}... - {e}")
        return None


def collect_dataset(
    data: List[Dict],
    output_path: str,
    max_queries: Optional[int] = None,
):
    """
    批量收集训练数据。

    Args:
        data: 输入数据列表
        output_path: 输出文件路径
        max_queries: 最大收集数量（可选）
    """
    print(f"\n开始收集训练数据...")
    print(f"  输入数据量: {len(data)}")
    if max_queries:
        print(f"  最大收集数: {max_queries}")
    print()

    # 初始化 agent
    print("初始化 ZVAgent...")
    try:
        agent = initialize_agent()
        print("  OK Agent 初始化成功")
    except Exception as e:
        print(f"  X Agent 初始化失败: {e}")
        print("  请确保 ZVAgent 配置正确（config.json）")
        return

    # 获取可用 skill 列表
    available_skills = [e.skill.name for e in agent.skill_manager.list_skills()]
    print(f"  可用 skill 数量: {len(available_skills)}")
    print()

    # 收集数据
    dataset = []
    success_count = 0
    error_count = 0

    for i, item in enumerate(tqdm(data, desc="收集数据")):
        if max_queries and i >= max_queries:
            break

        query = item.get("user_message", "")
        if not query:
            continue

        record = collect_single_query(
            agent=agent,
            query=query,
            available_skills=available_skills,
        )

        if record:
            dataset.append(record)
            success_count += 1
        else:
            error_count += 1

    # 保存结果
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for item in dataset:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # 统计
    skill_counts = {}
    for item in dataset:
        for skill in item.get("selected_skills", []):
            skill_counts[skill] = skill_counts.get(skill, 0) + 1

    print(f"\n收集完成!")
    print(f"  成功: {success_count}")
    print(f"  失败: {error_count}")
    print(f"  总数据量: {len(dataset)} 条")
    if output_path:
        print(f"  保存到: {output_path}")

    # 显示 skill 分布
    if skill_counts:
        print(f"\nSkill 分布:")
        for skill, count in sorted(skill_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {skill}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Phase B 自动对话数据收集器")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).parent / "synthetic_data.jsonl"),
        help="输入文件路径（synthetic_data.jsonl）",
    )
    parser.add_argument(
        "--output",
        default=str(Path(__file__).parent / "real_data.jsonl"),
        help="输出文件路径（默认: real_data.jsonl）",
    )
    parser.add_argument(
        "--max-queries",
        type=int,
        default=None,
        help="最大收集数量（默认: 全部）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式，只收集 1 条数据",
    )

    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    # 检查输入文件
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}")
        print("请先运行 synthetic_data_generator.py 生成数据")
        return

    # 加载数据
    print(f"加载输入文件: {input_path}")
    data = load_synthetic_data(str(input_path))
    print(f"  加载了 {len(data)} 条数据")

    # 试运行模式
    if args.dry_run:
        args.max_queries = 1
        print("\n试运行模式：只收集 1 条数据")

    # 收集数据
    collect_dataset(
        data=data,
        output_path=str(output_path),
        max_queries=args.max_queries,
    )

    # 显示示例
    if output_path.exists():
        print(f"\n收集示例:")
        with open(output_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= 3:
                    break
                item = json.loads(line)
                print(f"\n  [{i+1}] 用户请求: {item['user_message']}")
                print(f"      选择的 skills: {item['selected_skills']}")


if __name__ == "__main__":
    main()
