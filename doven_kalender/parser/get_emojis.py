"""Assign emojis to calendar entries using a lazily selected LLM provider."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from doven_kalender.generator.generator import create_llm

DEFAULT_PROVIDER = "mistral"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"


def load_llm(provider: str = DEFAULT_PROVIDER, model: str | None = None, env_file: Path | None = None) -> Any:
    """Compatibility wrapper that creates a provider client.

    Loads a local `.env` file (if provided) then returns a concrete LLM
    implementation from the central `create_llm()` factory.
    """

    load_env_file(env_file)
    return create_llm(provider, model)


def load_env_file(env_file: Path | None = None) -> bool:
    candidate = env_file or DEFAULT_ENV_FILE
    if not candidate.exists():
        return False

    for raw_line in candidate.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()

        key, separator, value = line.partition("=")
        if not separator:
            continue

        key = key.strip()
        value = value.strip()
        if not key:
            continue

        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]

        os.environ.setdefault(key, value)

    return True


def load_llm(provider: str = DEFAULT_PROVIDER, model: str | None = None, env_file: Path | None = None) -> LazyEmojiLLM:
    load_env_file(env_file)
    return LazyEmojiLLM(provider=provider, model=model)


def build_emoji_prompt(entries: Sequence[Mapping[str, Any]]) -> str:
    lines = [
        "Assign one relevant emoji to each calendar entry.",
        "Return valid JSON only in this exact shape:",
        '{"emojis": ["😀", "🎉"]}',
        "Use exactly one emoji per entry and keep the same order as the input.",
        "",
        "Entries:",
    ]
    for index, entry in enumerate(entries, start=1):
        title = str(entry.get("title", "")).strip()
        description = str(entry.get("description", "")).strip()
        lines.append(f"{index}. Title: {title}")
        if description:
            lines.append(f"   Description: {description}")

    return "\n".join(lines)


def extract_emoji_list(raw_output: str) -> list[str]:
    text = raw_output.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("Emoji provider response must be a JSON object")

    emojis = parsed.get("emojis")
    if not isinstance(emojis, list) or not all(isinstance(item, str) for item in emojis):
        raise ValueError("Emoji provider response must contain an 'emojis' list of strings")

    return emojis


def assign_emojis_to_entries(
    entries: Sequence[Mapping[str, Any]],
    provider: str = DEFAULT_PROVIDER,
    model: str | None = None,
    env_file: Path | None = None,
) -> list[dict[str, Any]]:
    entries_list = [dict(entry) for entry in entries]
    if not entries_list:
        return entries_list

    llm = load_llm(provider=provider, model=model, env_file=env_file)
    emojis = extract_emoji_list(llm.generate(build_emoji_prompt(entries_list)))
    if len(emojis) != len(entries_list):
        raise ValueError("LLM returned a different number of emojis than input entries")

    for entry, emoji in zip(entries_list, emojis, strict=True):
        entry["emoji"] = emoji

    return entries_list


def assign_emojis_to_calendar(data: Mapping[str, Sequence[Mapping[str, Any]]], provider: str = DEFAULT_PROVIDER, model: str | None = None, env_file: Path | None = None) -> dict[str, list[dict[str, Any]]]:
    return {
        side: assign_emojis_to_entries(entries, provider=provider, model=model, env_file=env_file)
        for side, entries in data.items()
    }


def read_calendar_json(json_file: Path) -> dict[str, list[dict[str, Any]]]:
    with json_file.open(encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise TypeError("Calendar JSON must contain an object at the top level")

    return {
        "left": [dict(entry) for entry in data.get("left", [])],
        "right": [dict(entry) for entry in data.get("right", [])],
    }


def write_calendar_json(json_file: Path, data: Mapping[str, Sequence[Mapping[str, Any]]]) -> None:
    with json_file.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=4)


def add_emojis_to_json(
    input_json: Path,
    output_json: Path | None = None,
    provider: str = DEFAULT_PROVIDER,
    model: str | None = None,
    env_file: Path | None = None,
) -> dict[str, list[dict[str, Any]]]:
    calendar_data = read_calendar_json(input_json)
    updated_data = assign_emojis_to_calendar(calendar_data, provider=provider, model=model, env_file=env_file)
    destination = output_json or input_json
    write_calendar_json(destination, updated_data)
    return updated_data


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path, help="Path to the input calendar JSON file")
    parser.add_argument("output_json", nargs="?", type=Path, help="Optional output path; defaults to overwriting the input file")
    parser.add_argument("--provider", choices=("mistral", "google"), default=DEFAULT_PROVIDER, help="LLM provider to use")
    parser.add_argument("--model", help="Optional provider-specific model override")
    parser.add_argument("--env-file", type=Path, help="Optional path to the .env file")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    add_emojis_to_json(
        args.input_json,
        output_json=args.output_json,
        provider=args.provider,
        model=args.model,
        env_file=args.env_file,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
