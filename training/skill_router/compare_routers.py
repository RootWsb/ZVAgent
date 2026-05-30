#!/usr/bin/env python3
"""
Compare legacy skill routing against a trained SkillRouter.

The script uses one shared question set, runs/loads old-router selections,
gets new-router predictions, computes metrics against ideal_skills, and writes
SVG charts plus JSON/CSV details.

Examples:
    python compare_routers.py --input labeled_data.jsonl
    python compare_routers.py --input synthetic_data.jsonl --run-old-router
"""

import argparse
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from training.skill_router.model import SkillRouter


DEFAULT_DIR = Path(__file__).parent
DEFAULT_CHECKPOINT_ROOT = DEFAULT_DIR / "checkpoints" / "skill_router"
PLACEHOLDER_SKILLS = {"...", "skill-a", "skill-b", "skill1", "skill2", "skill名称"}


def load_jsonl(path: Path) -> List[Dict]:
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return data


def load_skill_names(skill_index_path: Path) -> List[str]:
    with open(skill_index_path, "r", encoding="utf-8") as f:
        skill_index = json.load(f)
    names = [None] * len(skill_index)
    for name, index in skill_index.items():
        index = int(index)
        if 0 <= index < len(names):
            names[index] = name
    return [name or f"<missing-{i}>" for i, name in enumerate(names)]


def clean_skills(skills: List[str], hide_placeholders: bool = True) -> List[str]:
    seen = set()
    cleaned = []
    for skill in skills or []:
        skill = str(skill).strip()
        if not skill:
            continue
        if hide_placeholders and skill in PLACEHOLDER_SKILLS:
            continue
        if skill not in seen:
            cleaned.append(skill)
            seen.add(skill)
    return cleaned


def get_ideal_skills(sample: Dict) -> List[str]:
    if isinstance(sample.get("ideal_skills"), list):
        return sample["ideal_skills"]
    judge = sample.get("judge", {})
    if isinstance(judge, dict) and isinstance(judge.get("correct_skills"), list):
        return judge["correct_skills"]
    return []


def predict_new_router(
    model: SkillRouter,
    text: str,
    skill_names: List[str],
    top_k: int,
    threshold: float,
    hide_placeholders: bool,
) -> List[str]:
    model.eval()
    inputs = model.tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True,
    )
    device = next(model.parameters()).device
    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.no_grad():
        scores = model(**inputs).squeeze(0).detach().cpu()

    top_indices = scores.topk(min(top_k, len(skill_names))).indices.tolist()
    predicted = []
    for index in top_indices:
        skill = skill_names[index]
        score = float(scores[index].item())
        if score >= threshold:
            predicted.append(skill)
    return clean_skills(predicted, hide_placeholders=hide_placeholders)


def build_legacy_router():
    """Initialize ZVAgent SkillManager for optional live old-router evaluation."""
    old_cwd = os.getcwd()
    os.chdir(PROJECT_ROOT)
    try:
        from config import load_config
        from agent.skills import SkillManager

        load_config()
        return SkillManager()
    finally:
        os.chdir(old_cwd)


def predict_old_router(skill_manager, text: str) -> List[str]:
    return skill_manager.select_relevant_skills(text)


def metric_one(predicted: List[str], ideal: List[str]) -> Dict:
    pred_set = set(predicted)
    ideal_set = set(ideal)
    overlap = pred_set & ideal_set

    if pred_set:
        precision = len(overlap) / len(pred_set)
    else:
        precision = 1.0 if not ideal_set else 0.0

    if ideal_set:
        recall = len(overlap) / len(ideal_set)
    else:
        recall = 1.0 if not pred_set else 0.0

    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "exact": 1.0 if pred_set == ideal_set else 0.0,
        "selected_count": len(pred_set),
        "ideal_count": len(ideal_set),
        "extra_count": len(pred_set - ideal_set),
        "missed_count": len(ideal_set - pred_set),
    }


def mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def aggregate(rows: List[Dict], prefix: str) -> Dict:
    return {
        "precision": mean([row[f"{prefix}_precision"] for row in rows]),
        "recall": mean([row[f"{prefix}_recall"] for row in rows]),
        "f1": mean([row[f"{prefix}_f1"] for row in rows]),
        "exact": mean([row[f"{prefix}_exact"] for row in rows]),
        "avg_selected": mean([row[f"{prefix}_selected_count"] for row in rows]),
        "avg_extra": mean([row[f"{prefix}_extra_count"] for row in rows]),
        "avg_missed": mean([row[f"{prefix}_missed_count"] for row in rows]),
    }


def write_csv(path: Path, rows: List[Dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "index",
        "user_message",
        "ideal_skills",
        "old_skills",
        "new_skills",
        "old_precision",
        "old_recall",
        "old_f1",
        "old_exact",
        "old_selected_count",
        "old_extra_count",
        "old_missed_count",
        "new_precision",
        "new_recall",
        "new_f1",
        "new_exact",
        "new_selected_count",
        "new_extra_count",
        "new_missed_count",
    ]
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def svg_grouped_bar(
    path: Path,
    title: str,
    labels: List[str],
    series: List[Tuple[str, List[float], str]],
    max_value: Optional[float] = None,
    value_format: str = "{:.2f}",
):
    width = 980
    height = 520
    margin_left = 90
    margin_right = 40
    margin_top = 80
    margin_bottom = 110
    chart_w = width - margin_left - margin_right
    chart_h = height - margin_top - margin_bottom
    max_value = max_value or max(max(values) for _, values, _ in series) or 1.0
    max_value = max(max_value, 1e-6)

    group_w = chart_w / max(1, len(labels))
    bar_gap = 5
    bar_w = max(8, (group_w - 24) / max(1, len(series)) - bar_gap)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfbf8"/>',
        f'<text x="{width/2}" y="38" text-anchor="middle" font-size="24" font-family="Segoe UI, Arial" fill="#222">{title}</text>',
    ]

    # Grid and y labels.
    for i in range(6):
        value = max_value * i / 5
        y = margin_top + chart_h - (value / max_value) * chart_h
        parts.append(f'<line x1="{margin_left}" y1="{y:.1f}" x2="{width-margin_right}" y2="{y:.1f}" stroke="#ddd"/>')
        parts.append(f'<text x="{margin_left-12}" y="{y+4:.1f}" text-anchor="end" font-size="12" font-family="Segoe UI, Arial" fill="#555">{value_format.format(value)}</text>')

    parts.append(f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top+chart_h}" stroke="#999"/>')
    parts.append(f'<line x1="{margin_left}" y1="{margin_top+chart_h}" x2="{width-margin_right}" y2="{margin_top+chart_h}" stroke="#999"/>')

    for label_i, label in enumerate(labels):
        group_x = margin_left + label_i * group_w + 12
        for series_i, (name, values, color) in enumerate(series):
            value = values[label_i]
            bar_h = (value / max_value) * chart_h
            x = group_x + series_i * (bar_w + bar_gap)
            y = margin_top + chart_h - bar_h
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{color}" rx="2"/>')
            parts.append(f'<text x="{x + bar_w/2:.1f}" y="{y-6:.1f}" text-anchor="middle" font-size="11" font-family="Segoe UI, Arial" fill="#333">{value_format.format(value)}</text>')

        label_x = margin_left + label_i * group_w + group_w / 2
        safe_label = label.replace("&", "&amp;")
        parts.append(f'<text x="{label_x:.1f}" y="{margin_top+chart_h+28}" text-anchor="middle" font-size="13" font-family="Segoe UI, Arial" fill="#333">{safe_label}</text>')

    legend_x = margin_left
    legend_y = height - 44
    for name, _, color in series:
        parts.append(f'<rect x="{legend_x}" y="{legend_y-12}" width="14" height="14" fill="{color}" rx="2"/>')
        parts.append(f'<text x="{legend_x+20}" y="{legend_y}" font-size="14" font-family="Segoe UI, Arial" fill="#333">{name}</text>')
        legend_x += 150

    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def make_charts(output_dir: Path, summary: Dict, rows: List[Dict]):
    output_dir.mkdir(parents=True, exist_ok=True)
    old = summary["old"]
    new = summary["new"]

    svg_grouped_bar(
        output_dir / "quality_metrics.svg",
        "Old Router vs New Router: Quality Metrics",
        ["precision", "recall", "f1", "exact"],
        [
            ("old", [old["precision"], old["recall"], old["f1"], old["exact"]], "#8c8c8c"),
            ("new", [new["precision"], new["recall"], new["f1"], new["exact"]], "#2f80ed"),
        ],
        max_value=1.0,
    )

    svg_grouped_bar(
        output_dir / "selection_efficiency.svg",
        "Selection Efficiency",
        ["selected", "extra", "missed"],
        [
            ("old", [old["avg_selected"], old["avg_extra"], old["avg_missed"]], "#8c8c8c"),
            ("new", [new["avg_selected"], new["avg_extra"], new["avg_missed"]], "#2f80ed"),
        ],
        value_format="{:.1f}",
    )

    ideal_counts = Counter()
    old_counts = Counter()
    new_counts = Counter()
    for row in rows:
        ideal_counts.update(row["ideal_skills"])
        old_counts.update(row["old_skills"])
        new_counts.update(row["new_skills"])

    top_skills = [
        skill
        for skill, _ in (ideal_counts + old_counts + new_counts).most_common(12)
        if skill not in PLACEHOLDER_SKILLS
    ][:10]
    if top_skills:
        svg_grouped_bar(
            output_dir / "skill_frequency.svg",
            "Top Skill Frequency",
            top_skills,
            [
                ("ideal", [ideal_counts[s] for s in top_skills], "#27ae60"),
                ("old", [old_counts[s] for s in top_skills], "#8c8c8c"),
                ("new", [new_counts[s] for s in top_skills], "#2f80ed"),
            ],
            value_format="{:.0f}",
        )


def main():
    parser = argparse.ArgumentParser(description="Compare old and new skill routers")
    parser.add_argument(
        "--input",
        default=str(DEFAULT_DIR / "labeled_data.jsonl"),
        help="question set JSONL; should contain user_message and ideal_skills",
    )
    parser.add_argument(
        "--checkpoint",
        default=str(DEFAULT_CHECKPOINT_ROOT / "best"),
        help="new router checkpoint directory",
    )
    parser.add_argument(
        "--skill-index",
        default=str(DEFAULT_CHECKPOINT_ROOT / "skill_index.json"),
        help="skill_index.json path",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_DIR / "comparison_report"),
        help="directory for JSON/CSV/SVG outputs",
    )
    parser.add_argument("--top-k", type=int, default=5, help="new router top-k")
    parser.add_argument("--threshold", type=float, default=0.3, help="new router threshold")
    parser.add_argument("--max-samples", type=int, default=None, help="limit number of questions")
    parser.add_argument("--device", default=None, help="cpu, cuda, or auto")
    parser.add_argument(
        "--run-old-router",
        action="store_true",
        help="call current ZVAgent legacy router instead of using selected_skills from input",
    )
    parser.add_argument(
        "--show-placeholders",
        action="store_true",
        help="include placeholder labels from imperfect training data",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    samples = load_jsonl(input_path)
    if args.max_samples:
        samples = samples[: args.max_samples]

    hide_placeholders = not args.show_placeholders
    skill_names = load_skill_names(Path(args.skill_index))
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")

    print(f"Input: {input_path} ({len(samples)} samples)")
    print(f"Checkpoint: {args.checkpoint}")
    print(f"Skill index: {args.skill_index} ({len(skill_names)} labels)")
    print(f"Device: {device}")
    print(f"New router: top_k={args.top_k}, threshold={args.threshold}")

    new_model = SkillRouter.load_classifier(args.checkpoint, device=device)
    old_router = build_legacy_router() if args.run_old_router else None

    rows = []
    for index, sample in enumerate(samples):
        user_message = sample.get("user_message", "")
        if not user_message:
            continue

        ideal = clean_skills(get_ideal_skills(sample), hide_placeholders=hide_placeholders)
        if args.run_old_router:
            old_skills = predict_old_router(old_router, user_message)
        else:
            old_skills = sample.get("selected_skills", [])
        old_skills = clean_skills(old_skills, hide_placeholders=hide_placeholders)

        new_skills = predict_new_router(
            new_model,
            user_message,
            skill_names,
            top_k=args.top_k,
            threshold=args.threshold,
            hide_placeholders=hide_placeholders,
        )

        old_metrics = metric_one(old_skills, ideal)
        new_metrics = metric_one(new_skills, ideal)

        row = {
            "index": index,
            "user_message": user_message,
            "ideal_skills": ideal,
            "old_skills": old_skills,
            "new_skills": new_skills,
        }
        for key, value in old_metrics.items():
            row[f"old_{key}"] = value
        for key, value in new_metrics.items():
            row[f"new_{key}"] = value
        rows.append(row)

    summary = {
        "input": str(input_path),
        "samples": len(rows),
        "new_router": {
            "checkpoint": str(args.checkpoint),
            "top_k": args.top_k,
            "threshold": args.threshold,
        },
        "old_source": "live_legacy_router" if args.run_old_router else "input.selected_skills",
        "old": aggregate(rows, "old"),
        "new": aggregate(rows, "new"),
    }
    old_avg = summary["old"]["avg_selected"]
    new_avg = summary["new"]["avg_selected"]
    summary["skill_count_reduction_ratio"] = (
        (old_avg - new_avg) / old_avg if old_avg else 0.0
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    write_csv(output_dir / "samples.csv", rows)
    make_charts(output_dir, summary, rows)

    print("\nSummary:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nWrote report to: {output_dir}")
    print("Charts:")
    print(f"  {output_dir / 'quality_metrics.svg'}")
    print(f"  {output_dir / 'selection_efficiency.svg'}")
    print(f"  {output_dir / 'skill_frequency.svg'}")


if __name__ == "__main__":
    main()
