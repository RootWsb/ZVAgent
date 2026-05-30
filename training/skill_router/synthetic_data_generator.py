#!/usr/bin/env python3
"""
Skill Router 合成训练数据生成器

用 DeepSeek V4 Pro 批量生成 (用户请求, 理想 skills) 对，
用于训练 SkillRouter 分类器。

用法：
    python synthetic_data_generator.py --tasks tasks.txt --output synthetic_data.jsonl

环境变量：
    DEEPSEEK_API_KEY: DeepSeek API 密钥

依赖：
    pip install requests tqdm
"""

import argparse
import json
import os
import random
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from tqdm import tqdm

# ============================================
# 配置
# ============================================

DEFAULT_MODEL = "deepseek-v4-pro"
DEFAULT_API_BASE = "https://inferaichat.com/v1"
DEFAULT_NUM_VARIANTS = 5
DEFAULT_CONCURRENCY = 5  # 并发请求数
MAX_CONSECUTIVE_FAILURES = 12

# 模拟用户请求的 prompt
SIMULATION_PROMPT = """你是一个中文用户。根据任务描述，生成一个口语化的中文用户请求（20-100字）。

任务：{task_description}

可用 skills：
{skills_catalog}

输出格式（只输出JSON，不要有其他文字）：
{{"user_message": "口语化的中文请求", "ideal_skills": ["skill名称"], "reasoning": "为什么需要这些skill"}}

注意：
- user_message 必须是中文，口语化，20-100字
- ideal_skills 从上面的 skills 中选择（0-3个），很多问题不需要任何 skill（输出空数组 []）
- 直接输出JSON，不要有任何其他文字"""


def get_skills_catalog(skills_dir: str = None) -> str:
    """从 skills 目录读取所有 skill 的名称和描述，生成 catalog 文本"""
    if skills_dir is None:
        # 从 training/skill_router/ 向上两级到 ZVagent/skills/
        skills_dir = Path(__file__).parent.parent.parent / "skills"
    else:
        skills_dir = Path(skills_dir)

    catalog_lines = []
    if not skills_dir.exists():
        return ""

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        name = skill_dir.name
        description = ""
        try:
            content = skill_md.read_text(encoding="utf-8")
            lines = content.split("\n")
            in_frontmatter = False
            for line in lines:
                stripped = line.strip()
                if stripped == "---":
                    in_frontmatter = not in_frontmatter
                    continue
                if in_frontmatter and stripped.startswith("description:"):
                    description = stripped[len("description:"):].strip()[:150]
                    break
                if not in_frontmatter and stripped and not stripped.startswith("#"):
                    description = stripped[:150]
                    break
        except Exception:
            pass

        catalog_lines.append(f"- {name}: {description}")

    return "\n".join(catalog_lines)


def load_tasks(tasks_path: str) -> List[str]:
    """从 tasks.txt 加载任务描述（每行一个，忽略空行和注释）"""
    tasks = []
    with open(tasks_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                tasks.append(line)
    return tasks


def log_error(log_path: Optional[Path], message: str):
    """Write debug details to a UTF-8 log file without risking console encoding issues."""
    if not log_path:
        return
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(message.rstrip() + "\n")


def normalize_api_base(api_base: str) -> str:
    """Accept either https://host or https://host/v1 and build one clean chat URL."""
    return api_base.rstrip("/")


def repair_mojibake(text: str) -> str:
    """
    Repair common UTF-8 text that was accidentally decoded as latin-1/cp1252.

    Some proxy APIs occasionally return strings such as "å¸®æ" instead of
    "帮我". If repair fails, keep the original text.
    """
    if not isinstance(text, str):
        return text
    suspicious = sum(text.count(ch) for ch in ("Ã", "Â", "å", "æ", "ç", "è", "é", "ï¼"))
    if suspicious < 2:
        return text
    for encoding in ("latin1", "cp1252"):
        try:
            repaired = text.encode(encoding).decode("utf-8")
            if repaired and repaired != text:
                return repaired
        except UnicodeError:
            continue
    return text


def sanitize_generated_item(item: Dict) -> Dict:
    """Normalize generated fields before validation and persistence."""
    item = dict(item)
    if isinstance(item.get("user_message"), str):
        item["user_message"] = repair_mojibake(item["user_message"]).strip()
    if isinstance(item.get("reasoning"), str):
        item["reasoning"] = repair_mojibake(item["reasoning"]).strip()
    if not isinstance(item.get("ideal_skills"), list):
        item["ideal_skills"] = []
    item["ideal_skills"] = [
        str(skill).strip()
        for skill in item.get("ideal_skills", [])
        if str(skill).strip()
    ][:3]
    return item


def call_deepseek_api(
    prompt: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
    api_base: str = DEFAULT_API_BASE,
    temperature: float = 0.9,
    max_tokens: int = 1024,
    log_path: Optional[Path] = None,
) -> str:
    """调用 DeepSeek API"""
    api_base = normalize_api_base(api_base)
    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            if response.status_code >= 400:
                body = response.text[:1000]
                raise RuntimeError(f"HTTP {response.status_code}: {body}")
            result = response.json()
            message = result["choices"][0]["message"]
            # 中转站兼容：deepseek-v4-pro 的 thinking 模式
            # 会把最终答案放在 content，思考过程放在 reasoning_content
            # 优先取 content（最终答案），如果没有再取 reasoning_content
            content = message.get("content") or message.get("reasoning_content") or ""
            # 只要有内容就返回，让 parse_llm_response 处理解析
            if content:
                return repair_mojibake(content)
            raise ValueError(f"API returned empty message content: {result}")
        except Exception as e:
            if attempt < 2:
                log_error(
                    log_path,
                    f"[API attempt {attempt+1}/3] {type(e).__name__}: {str(e)}",
                )
                time.sleep(2)
                continue
            # 最后一次尝试失败，记录完整错误
            log_error(
                log_path,
                f"[API final failure] {type(e).__name__}: {str(e)}",
            )
            raise

    # 如果所有尝试都失败，返回空字符串
    return ""


def parse_llm_response(response: str) -> Dict:
    """解析 LLM 返回的 JSON，处理各种格式问题"""
    if not response or not response.strip():
        raise ValueError("LLM 返回空响应")

    response = response.strip()
    if response.startswith("```"):
        lines = response.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        response = "\n".join(lines).strip()

    # 先尝试直接解析
    try:
        return sanitize_generated_item(json.loads(response))
    except json.JSONDecodeError:
        pass

    # 尝试提取 JSON 部分：找到第一个 { 和最后一个 }
    start = response.find('{')
    end = response.rfind('}')
    if start != -1 and end != -1 and end > start:
        json_str = response[start:end+1]
        try:
            return sanitize_generated_item(json.loads(json_str))
        except json.JSONDecodeError:
            pass

    # 如果是 reasoning_content，尝试提取其中的 JSON
    # 这种情况下 JSON 可能被截断，需要构造默认值
    if '"user_message"' in response:
        # 尝试提取 user_message 和 ideal_skills
        import re
        user_msg_match = re.search(r'"user_message"\s*:\s*"([^"]*)"', response)
        ideal_skills_match = re.search(r'"ideal_skills"\s*:\s*\[([^\]]*)\]', response)

        if user_msg_match:
            user_message = user_msg_match.group(1)
            ideal_skills = []
            if ideal_skills_match:
                skills_str = ideal_skills_match.group(1)
                ideal_skills = [s.strip().strip('"') for s in skills_str.split(',') if s.strip()]

            return sanitize_generated_item({
                "user_message": user_message,
                "ideal_skills": ideal_skills,
                "reasoning": "从 reasoning_content 提取",
            })

    raise ValueError(f"无法解析 LLM 响应: {response[:1000]}")


def generate_single_task(
    task: str,
    skills_catalog: str,
    api_key: str,
    model: str,
    api_base: str,
    variant_index: int = 0,
    log_path: Optional[Path] = None,
) -> Dict:
    """为单个任务生成一条训练数据"""
    prompt = SIMULATION_PROMPT.format(
        task_description=task,
        skills_catalog=skills_catalog,
    )
    response = call_deepseek_api(
        prompt=prompt,
        api_key=api_key,
        model=model,
        api_base=api_base,
        log_path=log_path,
    )
    result = parse_llm_response(response)

    # 验证格式
    if "user_message" not in result:
        raise ValueError(f"缺少 user_message: {result}")
    if "ideal_skills" not in result:
        result["ideal_skills"] = []

    return {
        "user_message": result["user_message"],
        "ideal_skills": result.get("ideal_skills", []),
        "reasoning": result.get("reasoning", ""),
        "source_task": task,
        "variant_index": variant_index,
        "generation_method": "synthetic",
    }


def load_existing_output(output_path: Optional[str]) -> Tuple[List[Dict], set]:
    """Load existing JSONL output and return records plus completed task variants."""
    if not output_path:
        return [], set()
    path = Path(output_path)
    if not path.exists():
        return [], set()

    records = []
    completed = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            records.append(item)
            completed.add((item.get("source_task", ""), int(item.get("variant_index", 0))))
    return records, completed


def generate_dataset(
    tasks: List[str],
    skills_catalog: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
    api_base: str = DEFAULT_API_BASE,
    num_variants: int = DEFAULT_NUM_VARIANTS,
    output_path: str = None,
    resume: bool = False,
    max_consecutive_failures: int = MAX_CONSECUTIVE_FAILURES,
) -> List[Dict]:
    """批量生成训练数据"""
    output_file = Path(output_path) if output_path else None
    log_path = output_file.with_suffix(".errors.log") if output_file else Path("_synthetic_data_errors.log")

    if resume:
        dataset, completed = load_existing_output(output_path)
    else:
        dataset, completed = [], set()
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text("", encoding="utf-8")
        if log_path.exists():
            log_path.write_text("", encoding="utf-8")

    total_calls = len(tasks) * num_variants
    remaining_calls = total_calls - len(completed)

    print(f"\n开始生成训练数据...")
    print(f"  任务数: {len(tasks)}")
    print(f"  每个任务生成 {num_variants} 个变体")
    print(f"  总请求数: {total_calls}")
    if resume and completed:
        print(f"  断点续跑: 已跳过 {len(completed)} 条，剩余 {remaining_calls} 条")
    print(f"  模型: {model}")
    print(f"  错误日志: {log_path}")
    print()

    success_count = 0
    error_count = 0
    consecutive_failures = 0

    for task in tqdm(tasks, desc="处理任务"):
        for variant_idx in range(num_variants):
            if (task, variant_idx) in completed:
                continue
            try:
                result = generate_single_task(
                    task=task,
                    skills_catalog=skills_catalog,
                    api_key=api_key,
                    model=model,
                    api_base=api_base,
                    variant_index=variant_idx,
                    log_path=log_path,
                )
                dataset.append(result)
                success_count += 1
                consecutive_failures = 0

                if output_file:
                    with open(output_file, "a", encoding="utf-8") as f:
                        f.write(json.dumps(result, ensure_ascii=False) + "\n")

                # 简单限速：避免 API 限流
                time.sleep(0.1)

            except Exception as e:
                error_count += 1
                consecutive_failures += 1
                log_error(
                    log_path,
                    f"[Task failed] task={task!r} variant={variant_idx} "
                    f"error={type(e).__name__}: {str(e)}",
                )
                tqdm.write(f"  X failed: {task[:30]} ({type(e).__name__}: {str(e)[:80]})")
                if consecutive_failures >= max_consecutive_failures:
                    raise RuntimeError(
                        f"连续失败 {consecutive_failures} 次，已停止以避免浪费请求。"
                        f"请查看错误日志: {log_path}"
                    ) from e
                time.sleep(1)  # 失败后多等一会

    # 统计
    skill_counts = {}
    for item in dataset:
        for skill in item.get("ideal_skills", []):
            skill_counts[skill] = skill_counts.get(skill, 0) + 1

    print(f"\n生成完成!")
    print(f"  成功: {success_count}")
    print(f"  失败: {error_count}")
    print(f"  总数据量: {len(dataset)} 条")
    if output_path:
        print(f"  保存到: {output_file}")
    if error_count:
        print(f"  错误日志: {log_path}")

    # 显示 skill 分布
    if skill_counts:
        print(f"\nSkill 分布:")
        for skill, count in sorted(skill_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {skill}: {count}")

    return dataset


def main():
    parser = argparse.ArgumentParser(description="Skill Router 合成训练数据生成器")
    parser.add_argument(
        "--tasks",
        default=str(Path(__file__).parent / "tasks.txt"),
        help="任务描述文件路径 (默认: tasks.txt)",
    )
    parser.add_argument(
        "--output",
        default=str(Path(__file__).parent / "synthetic_data.jsonl"),
        help="输出文件路径 (默认: synthetic_data.jsonl)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"DeepSeek 模型名称 (默认: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--api-base",
        default=DEFAULT_API_BASE,
        help=f"API 基础 URL (默认: {DEFAULT_API_BASE})",
    )
    parser.add_argument(
        "--num-variants",
        type=int,
        default=DEFAULT_NUM_VARIANTS,
        help=f"每个任务生成的变体数 (默认: {DEFAULT_NUM_VARIANTS})",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="DeepSeek API 密钥 (也可通过 DEEPSEEK_API_KEY 环境变量设置)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式，只生成 1 个变体，用于验证",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="断点续跑：保留已有输出并跳过已经生成的 task/variant",
    )
    parser.add_argument(
        "--max-consecutive-failures",
        type=int,
        default=MAX_CONSECUTIVE_FAILURES,
        help=f"连续失败多少次后停止 (默认: {MAX_CONSECUTIVE_FAILURES})",
    )

    args = parser.parse_args()

    # 获取 API 密钥（优先使用命令行参数，其次环境变量，最后使用默认值）
    api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY", "sk-82124fde460ca67d359907f64155f4210f6cd4c33cfea4ea92b2c946f1ab0785")

    # 加载任务
    print(f"加载任务文件: {args.tasks}")
    tasks = load_tasks(args.tasks)
    print(f"  加载了 {len(tasks)} 个任务")

    # 生成 skill catalog
    print("生成 Skill 目录...")
    skills_catalog = get_skills_catalog()
    print(f"  发现 {skills_catalog.count('- ')} 个 skill")

    # 试运行模式
    if args.dry_run:
        args.num_variants = 1
        tasks = [tasks[0]]  # 只处理第一个任务
        print("\n试运行模式：只生成 1 个变体")
        print(f"任务示例: {tasks[0]}")

    # 生成数据
    dataset = generate_dataset(
        tasks=tasks,
        skills_catalog=skills_catalog,
        api_key=api_key,
        model=args.model,
        api_base=args.api_base,
        num_variants=args.num_variants,
        output_path=args.output,
        resume=args.resume,
        max_consecutive_failures=args.max_consecutive_failures,
    )

    # 显示示例（避免 GBK 编码错误）
    if dataset:
        with open("_samples_preview.txt", "w", encoding="utf-8") as f:
            f.write("生成示例:\n")
            for i, item in enumerate(dataset[:3], 1):
                f.write(f"\n  [{i}] 用户请求: {item['user_message']}\n")
                f.write(f"      理想 skills: {item['ideal_skills']}\n")
                f.write(f"      原始任务: {item['source_task'][:60]}...\n")
        print(f"\n生成示例已保存到 _samples_preview.txt")


if __name__ == "__main__":
    main()
