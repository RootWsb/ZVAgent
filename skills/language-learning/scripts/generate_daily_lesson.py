#!/usr/bin/env python3
"""Generate a practical daily language-learning lesson.

The script is deterministic and offline-friendly. It creates a structured
lesson shell that the agent can use directly or enrich during chat.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List


LANGUAGE_PACKS: Dict[str, Dict[str, Any]] = {
    "english": {
        "display": "English",
        "samples": [
            ("follow up", "跟进", "I will follow up with you tomorrow.", "work and study"),
            ("make progress", "取得进步", "You are making steady progress.", "growth"),
            ("be supposed to", "应该/按理说", "I am supposed to submit it today.", "daily tasks"),
            ("take a closer look", "仔细看看", "Let's take a closer look at this sentence.", "study"),
            ("feel confident about", "对...有信心", "I feel confident about speaking today.", "speaking"),
            ("work out", "解决/锻炼", "We can work out the problem together.", "problem solving"),
            ("in terms of", "就...而言", "In terms of pronunciation, this is better.", "analysis"),
            ("get used to", "习惯于", "I am getting used to speaking English every day.", "habits"),
        ],
        "patterns": [
            ("I used to ..., but now ...", "表达过去习惯和现在变化", "I used to translate every word, but now I try to think in English."),
            ("What I mean is ...", "澄清自己的意思", "What I mean is that I need more speaking practice."),
            ("It depends on ...", "表达取决于某条件", "It depends on how much time I have after work."),
        ],
    },
    "japanese": {
        "display": "Japanese",
        "samples": [
            ("お願いします", "拜托/请", "コーヒーを一つお願いします。", "polite request"),
            ("大丈夫です", "没关系/可以", "はい、大丈夫です。", "daily response"),
            ("もう一度", "再一次", "もう一度お願いします。", "clarification"),
            ("少しだけ", "只是一点点", "日本語を少しだけ話せます。", "self introduction"),
            ("探しています", "正在找", "駅を探しています。", "travel"),
            ("おすすめ", "推荐", "おすすめは何ですか。", "shopping"),
        ],
        "patterns": [
            ("Nをください / Nをお願いします", "礼貌请求某物", "水をください。 / コーヒーをお願いします。"),
            ("Nはどこですか", "询问地点", "トイレはどこですか。"),
            ("Vてもいいですか", "请求许可", "ここに座ってもいいですか。"),
        ],
    },
    "spanish": {
        "display": "Spanish",
        "samples": [
            ("me gustaría", "我想要", "Me gustaría practicar español.", "polite request"),
            ("tengo que", "我必须", "Tengo que estudiar veinte minutos.", "obligation"),
            ("poco a poco", "一点一点地", "Poco a poco hablo mejor.", "progress"),
            ("puedes repetir", "你能重复吗", "¿Puedes repetir, por favor?", "clarification"),
        ],
        "patterns": [
            ("Quiero + infinitivo", "表达想做某事", "Quiero aprender más palabras."),
            ("Tengo que + infinitivo", "表达必须做某事", "Tengo que practicar hoy."),
            ("Me gusta + infinitivo", "表达喜欢做某事", "Me gusta leer en español."),
        ],
    },
}

DEFAULT_PACK = LANGUAGE_PACKS["english"]


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "language-lesson"


def normalize_language(value: str) -> str:
    return (value or "English").strip().lower()


def get_pack(target_language: str) -> Dict[str, Any]:
    key = normalize_language(target_language)
    aliases = {
        "英语": "english",
        "english": "english",
        "en": "english",
        "日语": "japanese",
        "japanese": "japanese",
        "ja": "japanese",
        "日本語": "japanese",
        "西班牙语": "spanish",
        "spanish": "spanish",
        "es": "spanish",
    }
    return LANGUAGE_PACKS.get(aliases.get(key, key), {**DEFAULT_PACK, "display": target_language or "English"})


def load_mistakes(path: str | None, target_language: str) -> List[Dict[str, Any]]:
    if not path:
        return []
    mistake_path = Path(path).expanduser()
    if not mistake_path.exists():
        return []
    data = json.loads(mistake_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []
    target = normalize_language(target_language)
    return [
        item for item in data
        if isinstance(item, dict) and normalize_language(item.get("target_language", "")) in ("", target)
    ]


def choose_items(items: List[Any], count: int, offset_seed: str) -> List[Any]:
    if not items:
        return []
    offset = sum(ord(ch) for ch in offset_seed) % len(items)
    rotated = items[offset:] + items[:offset]
    return rotated[:count]


def render_vocab(pack: Dict[str, Any], args: argparse.Namespace) -> str:
    samples = choose_items(pack.get("samples", []), args.vocab_count, args.date + args.goal + args.topic)
    lines = ["| Word/Phrase | Meaning | Example | Note |", "|---|---|---|---|"]
    for phrase, meaning, example, note in samples:
        lines.append(f"| {phrase} | {meaning} | {example} | {note} |")
    return "\n".join(lines)


def render_pattern(pack: Dict[str, Any], args: argparse.Namespace) -> str:
    pattern = choose_items(pack.get("patterns", []), 1, args.date + args.level)[0]
    structure, meaning, example = pattern
    return "\n".join([
        f"- Structure: `{structure}`",
        f"- 用法: {meaning}",
        f"- Example: {example}",
        "- Common mistake: 不要只翻译单词，先确认句子的功能和语气。",
    ])


def render_reading(target_language: str, level: str, topic: str) -> str:
    pack = get_pack(target_language)
    name = pack["display"]
    topic_text = topic or "daily learning"
    if normalize_language(name) == "japanese":
        return (
            "今日は新しい言葉を三つ覚えます。短い文を声に出して読みます。"
            "分からない時は、もう一度お願いしますと言います。"
        )
    if normalize_language(name) == "spanish":
        return (
            f"Hoy estudio {name} poco a poco. Practico con un tema simple: {topic_text}. "
            "Leo en voz alta y escribo dos frases nuevas."
        )
    if level.lower() in ("beginner", "elementary", "a1", "a2"):
        return (
            f"Today I practice {name} for a short time. My topic is {topic_text}. "
            "I read slowly, say each sentence aloud, and write one useful phrase."
        )
    return (
        f"Today I focus on {topic_text}. Instead of memorizing isolated words, I turn each new phrase "
        "into a sentence I might actually say. This makes review easier and helps me speak more naturally."
    )


def render_review(mistakes: List[Dict[str, Any]]) -> str:
    if not mistakes:
        return "- No saved mistakes yet. Create one new correction card from today's output."
    lines = []
    for item in mistakes[-5:]:
        text = item.get("text", "")
        correction = item.get("correction", "")
        note = item.get("note", "")
        lines.append(f"- Rewrite: `{text}` -> `{correction}`. Rule: {note or 'explain the pattern in one sentence.'}")
    return "\n".join(lines)


def build_markdown(args: argparse.Namespace, mistakes: List[Dict[str, Any]]) -> str:
    pack = get_pack(args.target_language)
    title = f"{args.date} {pack['display']} Daily Lesson"
    topic = args.topic or args.goal
    return f"""# {title}

> Generated: {datetime.now().isoformat(timespec="seconds")}. Level: {args.level}. Goal: {args.goal}. Time: {args.minutes} minutes.

## Today's Focus

- Target language: {pack['display']}
- Native explanation language: {args.native_language}
- Topic: {topic}
- Output target: say or write 5 original sentences.

## Warm-up

- 用目标语言说一句今天的状态。
- 用目标语言说一句你今天想练什么。
- 把昨天或最近学过的一句话换一个主语重新说。

## Vocabulary

{render_vocab(pack, args)}

## Pattern

{render_pattern(pack, args)}

## Mini Reading

{render_reading(args.target_language, args.level, topic)}

## Output Practice

- Make 3 sentences with today's pattern.
- Answer this prompt in {pack['display']}: What is one thing you want to improve this week?
- Shadow the mini reading twice: once slowly, once naturally.

## Review

{render_review(mistakes)}

## Quick Check

- Translate one vocabulary example into {args.native_language}.
- Replace one word in the example sentence and keep the grammar correct.
- Explain the pattern in your own words.

## Homework

- Spend 5 minutes recording yourself or writing a 60-word note.
- Save one mistake with `review_mistakes.py add` if you notice a recurring issue.
"""


def update_index(knowledge_dir: Path, rel_path: str, title: str) -> None:
    index_path = knowledge_dir / "index.md"
    content = index_path.read_text(encoding="utf-8") if index_path.exists() else "# Knowledge Index\n"
    line = f"- [{title}]({rel_path}) - Language learning lesson"
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


def append_log(knowledge_dir: Path, title: str) -> None:
    log_path = knowledge_dir / "log.md"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"## [{date.today().isoformat()}] learn | {title}\n")


def write_lesson(args: argparse.Namespace, markdown: str) -> Path:
    if not args.workspace:
        raise ValueError("--workspace is required with --write")
    knowledge_dir = Path(args.workspace).expanduser() / "knowledge"
    target_dir = knowledge_dir / "language-learning" / "lessons"
    target_dir.mkdir(parents=True, exist_ok=True)
    pack = get_pack(args.target_language)
    title = f"{args.date} {pack['display']} Daily Lesson"
    target = target_dir / f"{args.date}-{slugify(pack['display'] + '-' + args.goal)}.md"
    target.write_text(markdown, encoding="utf-8")
    rel_path = str(target.relative_to(knowledge_dir)).replace("\\", "/")
    update_index(knowledge_dir, rel_path, title)
    append_log(knowledge_dir, title)
    return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", help="ZVAgent workspace path")
    parser.add_argument("--write", action="store_true", help="Write lesson into workspace knowledge base")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--target-language", default="English")
    parser.add_argument("--native-language", default="Chinese")
    parser.add_argument("--level", default="intermediate")
    parser.add_argument("--goal", default="speaking")
    parser.add_argument("--topic", default="")
    parser.add_argument("--minutes", type=int, default=20)
    parser.add_argument("--vocab-count", type=int, default=6)
    parser.add_argument("--mistakes", help="Path to mistakes.json")
    parser.add_argument("--json", action="store_true", help="When writing, print JSON payload")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mistakes_path = args.mistakes
    if not mistakes_path and args.workspace:
        mistakes_path = str(Path(args.workspace).expanduser() / "knowledge" / "language-learning" / "mistakes.json")
    mistakes = load_mistakes(mistakes_path, args.target_language)
    markdown = build_markdown(args, mistakes)
    if args.write:
        target = write_lesson(args, markdown)
        payload = {"status": "success", "path": str(target)}
        print(json.dumps(payload, ensure_ascii=False) if args.json else f"Wrote {target}")
    else:
        print(markdown, end="")


if __name__ == "__main__":
    main()

