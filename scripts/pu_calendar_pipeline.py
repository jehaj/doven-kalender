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


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left_month", help="Month name for the left side, for example 'maj'")
    parser.add_argument("right_month", help="Month name for the right side, for example 'juni'")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV_FILE, help="Path to the intermediate CSV output")
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_FILE, help="Path to the emoji-enriched JSON output")
    parser.add_argument("--document-url", help="Override DOCS_DOCUMENT_URL from .env")
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE, help="Path to the .env file")
    parser.add_argument("--provider", choices=("gemini", "mistral"), default="gemini", help="LLM provider for emoji assignment")
    parser.add_argument("--model", help="Optional provider-specific model override")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    load_env_file(args.env_file)

    document_url = args.document_url or os.getenv("DOCS_DOCUMENT_URL")
    if not document_url:
        print("Error: DOCS_DOCUMENT_URL environment variable not set.", file=sys.stderr)
        return 1

    extract_csv_from_odt(document_url, args.csv)
    convert_csv_to_json(args.csv, args.json, args.left_month, args.right_month)
    add_emojis_to_json(args.json, provider=args.provider, model=args.model, env_file=args.env_file)

    print(f"Wrote CSV to {args.csv}")
    print(f"Wrote emoji-enriched JSON to {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())