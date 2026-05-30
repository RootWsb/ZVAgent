#!/usr/bin/env python3
"""
Quick test utility for a trained SkillRouter checkpoint.

Examples:
    python test_router.py --text "帮我总结一下今天的 AI 新闻"
    python test_router.py --interactive
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

import torch

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from training.skill_router.model import SkillRouter


DEFAULT_CHECKPOINT_ROOT = Path(__file__).parent / "checkpoints" / "skill_router"
PLACEHOLDER_SKILLS = {"...", "skill-a", "skill-b", "skill1", "skill2", "skill名称"}


def load_skill_names(skill_index_path: Path) -> List[str]:
    with open(skill_index_path, "r", encoding="utf-8") as f:
        skill_index: Dict[str, int] = json.load(f)
    names = [None] * len(skill_index)
    for name, index in skill_index.items():
        if 0 <= int(index) < len(names):
            names[int(index)] = name
    return [name or f"<missing-{i}>" for i, name in enumerate(names)]


def predict_raw(model: SkillRouter, text: str, skill_names: List[str], top_k: int) -> List[Dict]:
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
    return [
        {
            "skill": skill_names[index],
            "score": round(float(scores[index].item()), 4),
        }
        for index in top_indices
    ]


def print_predictions(results: List[Dict], hide_placeholders: bool):
    shown = 0
    for item in results:
        if hide_placeholders and item["skill"] in PLACEHOLDER_SKILLS:
            continue
        shown += 1
        print(f"  {shown:>2}. {item['skill']:<34} {item['score']:.4f}")
    if shown == 0:
        print("  No non-placeholder skills in top-k results.")


def main():
    parser = argparse.ArgumentParser(description="Test a trained SkillRouter checkpoint")
    parser.add_argument(
        "--checkpoint",
        default=str(DEFAULT_CHECKPOINT_ROOT / "best"),
        help="checkpoint directory containing classifier.pt and config.json",
    )
    parser.add_argument(
        "--skill-index",
        default=str(DEFAULT_CHECKPOINT_ROOT / "skill_index.json"),
        help="skill_index.json path",
    )
    parser.add_argument("--text", default=None, help="single query to predict")
    parser.add_argument("--top-k", type=int, default=8, help="number of predictions to show")
    parser.add_argument("--threshold", type=float, default=0.0, help="display threshold")
    parser.add_argument("--device", default=None, help="cpu, cuda, or auto")
    parser.add_argument("--interactive", action="store_true", help="interactive REPL mode")
    parser.add_argument(
        "--show-placeholders",
        action="store_true",
        help="show placeholder labels such as skill-a/skill名称",
    )
    args = parser.parse_args()

    device = args.device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    checkpoint = Path(args.checkpoint)
    skill_index_path = Path(args.skill_index)
    skill_names = load_skill_names(skill_index_path)

    print(f"Loading checkpoint: {checkpoint}")
    print(f"Loading skill index: {skill_index_path} ({len(skill_names)} labels)")
    print(f"Device: {device}")
    model = SkillRouter.load_classifier(str(checkpoint), device=device)

    def run_query(text: str):
        results = predict_raw(model, text, skill_names, args.top_k)
        results = [item for item in results if item["score"] >= args.threshold]
        print(f"\nQuery: {text}")
        print_predictions(results, hide_placeholders=not args.show_placeholders)

    if args.text:
        run_query(args.text)

    if args.interactive or not args.text:
        print("\nEnter a query, or blank line / Ctrl+C to exit.")
        while True:
            try:
                text = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not text:
                break
            run_query(text)


if __name__ == "__main__":
    main()
