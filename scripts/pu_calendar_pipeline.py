"""One-shot pipeline for downloading PU's ODT and producing emoji-enriched JSON."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from doven_kalender.extractor.pu import extract_csv_from_odt
from doven_kalender.parser.convert_csv_to_json import convert_csv_to_json
from doven_kalender.parser.get_emojis import add_emojis_to_json, load_env_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_CSV_FILE = PROJECT_ROOT / "assets" / "output.csv"
DEFAULT_JSON_FILE = PROJECT_ROOT / "generator" / "data.json"
DEFAULT_ODT_FILE = PROJECT_ROOT / "assets" / "E26.docx.odt"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left_month", help="Month name for the left side, for example 'maj'")
    parser.add_argument("right_month", help="Month name for the right side, for example 'juni'")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV_FILE, help="Path to the intermediate CSV output")
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_FILE, help="Path to the emoji-enriched JSON output")
    parser.add_argument("--odt", "--odt-file", type=Path, default=None, help="Path to a local ODT document")
    parser.add_argument("--document-url", help="Override DOCS_DOCUMENT_URL from .env")
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE, help="Path to the .env file")
    parser.add_argument("--provider", choices=("gemini", "mistral"), default="gemini", help="LLM provider for emoji assignment")
    parser.add_argument("--model", help="Optional provider-specific model override")
    parser.add_argument("--temperature", type=float, default=None, help="Optional LLM temperature override")
    return parser.parse_args(argv)


def resolve_document_source(args: argparse.Namespace) -> Path | str | None:
    if args.odt is not None:
        return args.odt
    if args.document_url:
        return args.document_url

    env_odt = os.getenv("DOCS_ODT_FILE")
    if env_odt:
        return Path(env_odt)

    if DEFAULT_ODT_FILE.exists():
        return DEFAULT_ODT_FILE

    assets_dir = PROJECT_ROOT / "assets"
    if assets_dir.exists():
        odt_files = sorted(assets_dir.glob("*.odt"))
        if odt_files:
            return odt_files[0]

    env_url = os.getenv("DOCS_DOCUMENT_URL")
    if env_url:
        return env_url

    return None


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    load_env_file(args.env_file)

    document_source = resolve_document_source(args)
    if not document_source:
        print("Error: No ODT document source found (set DOCS_ODT_FILE, DOCS_DOCUMENT_URL, or provide assets/*.odt).", file=sys.stderr)
        return 1

    extract_csv_from_odt(document_source, args.csv)
    convert_csv_to_json(args.csv, args.json, args.left_month, args.right_month)
    kwargs = {"provider": args.provider, "model": args.model, "env_file": args.env_file}
    if args.temperature is not None:
        kwargs["temperature"] = args.temperature
    add_emojis_to_json(args.json, **kwargs)

    print(f"Wrote CSV to {args.csv}")
    print(f"Wrote emoji-enriched JSON to {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())