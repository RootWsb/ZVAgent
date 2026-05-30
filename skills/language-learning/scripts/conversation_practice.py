#!/usr/bin/env python3
"""Create a conversation practice card for language learning."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime
from pathlib import Path


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "conversation-practice"


def build_markdown(args: argparse.Namespace) -> str:
    return f"""# {args.date} {args.target_language} Conversation Practice

> Generated: {datetime.now().isoformat(timespec="seconds")}. Scenario: {args.scenario}. Level: {args.level}. Turns: {args.turns}.

## Coach Role

You are a patient {args.target_language} conversation partner. Keep each turn suitable for a {args.level} learner.

## Scenario

- Situation: {args.scenario}
- User goal: {args.goal}
- Style: {args.style}
- Native explanation language: {args.native_language}

## Rules

- Start with one short message in {args.target_language}.
- Ask one question at a time.
- After each user answer, give:
  - Corrected version.
  - More natural version.
  - One concise note in {args.native_language}.
  - Score: 1-5.
- Continue the role-play after the feedback.
- Save recurring mistakes with `review_mistakes.py add` when useful.

## Opening Turn

{opening_turn(args)}

## Useful Phrases

- Could you say that again?
- I mean ...
- Let me think for a second.
- What would you recommend?
- That sounds good to me.

## Completion Check

- The learner answered at least {args.turns} turns.
- The learner reused 2 new phrases.
- At least one correction was turned into a review card.
"""


def opening_turn(args: argparse.Namespace) -> str:
    scenario = args.scenario.lower()
    lang = args.target_language.lower()
    if "japanese" in lang or "日" in lang:
        if "coffee" in scenario or "cafe" in scenario or "カフェ" in scenario:
            return "いらっしゃいませ。ご注文は何にしますか。"
        return "こんにちは。今日はどんな練習をしたいですか。"
    if "spanish" in lang or "西班牙" in lang:
        return "Hola. ¿Qué te gustaría practicar hoy?"
    if "interview" in scenario:
        return "Thanks for coming in today. Could you briefly introduce yourself?"
    if "travel" in scenario:
        return "Hi, welcome. Where would you like to go today?"
    return "Hi. What would you like to practice today?"


def update_index(knowledge_dir: Path, rel_path: str, title: str) -> None:
    index_path = knowledge_dir / "index.md"
    content = index_path.read_text(encoding="utf-8") if index_path.exists() else "# Knowledge Index\n"
    line = f"- [{title}]({rel_path}) - Language conversation practice"
    if line in content:
        return
    heading = "## Language Learning"
    if heading in content:
        content = content.replace(heading, f"{heading}\n\n{line}", 1)
    else:
        if not content.endswith("\n"):
            content += "\n"
        content += f"\n{heading}\n\n{line}\n"
    index_path.write_text(content, encoding="utf-8")


def write_card(args: argparse.Namespace, markdown: str) -> Path:
    if not args.workspace:
        raise ValueError("--workspace is required with --write")
    knowledge_dir = Path(args.workspace).expanduser() / "knowledge"
    target_dir = knowledge_dir / "language-learning" / "conversations"
    target_dir.mkdir(parents=True, exist_ok=True)
    title = f"{args.date} {args.target_language} {args.scenario}"
    target = target_dir / f"{args.date}-{slugify(args.target_language + '-' + args.scenario)}.md"
    target.write_text(markdown, encoding="utf-8")
    rel_path = str(target.relative_to(knowledge_dir)).replace("\\", "/")
    update_index(knowledge_dir, rel_path, title)
    log_path = knowledge_dir / "log.md"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"## [{date.today().isoformat()}] practice | {title}\n")
    return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", help="ZVAgent workspace path")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--target-language", default="English")
    parser.add_argument("--native-language", default="Chinese")
    parser.add_argument("--level", default="intermediate")
    parser.add_argument("--scenario", default="daily conversation")
    parser.add_argument("--goal", default="speak more naturally")
    parser.add_argument("--style", default="friendly and realistic")
    parser.add_argument("--turns", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    markdown = build_markdown(args)
    if args.write:
        target = write_card(args, markdown)
        payload = {"status": "success", "path": str(target)}
        print(json.dumps(payload, ensure_ascii=False) if args.json else f"Wrote {target}")
    else:
        print(markdown, end="")


if __name__ == "__main__":
    main()

