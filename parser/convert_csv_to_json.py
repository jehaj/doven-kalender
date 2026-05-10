"""Convert calendar CSV rows to the JSON shape used by the poster generator."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections.abc import Sequence
from pathlib import Path

MONTH_NAME_TO_ABBR = {
    "januar": "jan",
    "februar": "feb",
    "marts": "mar",
    "april": "apr",
    "maj": "maj",
    "juni": "jun",
    "juli": "jul",
    "august": "aug",
    "september": "sep",
    "oktober": "okt",
    "november": "nov",
    "december": "dec",
}

MONTH_ABBRS = set(MONTH_NAME_TO_ABBR.values())
DATE_PATTERN = re.compile(r"(\d+)\s*\.?\s*([^\W\d_]+)", re.UNICODE)


def extract_date_parts(date_text: str) -> tuple[int, str] | None:
    """Extract the day number and month token from a date string."""

    match = DATE_PATTERN.search(date_text.strip())
    if match is None:
        return None

    return int(match.group(1)), match.group(2)


def normalize_month_name(month_name: str) -> str | None:
    """Normalize a Danish month name to its three-letter abbreviation."""

    normalized_month = month_name.strip().lower()
    if normalized_month in MONTH_ABBRS:
        return normalized_month

    return MONTH_NAME_TO_ABBR.get(normalized_month)


def normalize_date(date_text: str) -> str:
    """Normalize a date like '8. juli' to '8. jul'."""

    date_parts = extract_date_parts(date_text)
    if date_parts is None:
        return date_text.strip()

    day, month_name = date_parts
    month_abbr = normalize_month_name(month_name)
    if month_abbr is None:
        return date_text.strip()

    return f"{day}. {month_abbr}"


def normalize_target_month(month_name: str) -> str:
    """Normalize a target month to the abbreviation used in the JSON output."""

    normalized_month = normalize_month_name(month_name)
    if normalized_month is not None:
        return normalized_month

    raise ValueError(f"Unsupported month name: {month_name!r}")


def classify_month(month_abbr: str, left_month: str, right_month: str) -> str | None:
    """Return the output side for a normalized month, or None if it does not match."""

    if month_abbr == left_month:
        return "left"

    if month_abbr == right_month:
        return "right"

    return None


def build_entry(row: dict[str, str]) -> dict[str, str | None]:
    """Build the JSON entry for a single CSV row."""

    return {
        "date": normalize_date(row.get("Dato", "")),
        "emoji": None,
        "title": row.get("Titel", "").strip(),
        "description": row.get("Emne/aktivitet", "").strip(),
    }


def convert_csv_to_json(
    csv_file: Path,
    json_file: Path,
    left_month: str,
    right_month: str,
) -> None:
    """Convert a CSV file to the left/right JSON structure used by the poster.

    Args:
        csv_file: Path to the input CSV file.
        json_file: Path to the output JSON file.
        left_month: Month assigned to the ``left`` side.
        right_month: Month assigned to the ``right`` side.
    """

    left_month_abbr = normalize_target_month(left_month)
    right_month_abbr = normalize_target_month(right_month)
    if left_month_abbr == right_month_abbr:
        raise ValueError("left_month and right_month must refer to different months")

    data = {"left": [], "right": []}
    with csv_file.open(newline="", encoding="utf-8") as csv_handle:
        reader = csv.DictReader(csv_handle)
        for row in reader:
            row_date = row.get("Dato", "")
            date_parts = extract_date_parts(row_date)
            if date_parts is None:
                continue

            _, month_name = date_parts
            month_abbr = normalize_month_name(month_name)
            if month_abbr is None:
                continue

            side = classify_month(month_abbr, left_month_abbr, right_month_abbr)
            if side is None:
                continue

            data[side].append(build_entry(row))

    with json_file.open("w", encoding="utf-8") as json_handle:
        json.dump(data, json_handle, ensure_ascii=False, indent=4)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    """Parse command line arguments for the CSV conversion script."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path, help="Path to the input CSV file")
    parser.add_argument("output_json", type=Path, help="Path to the output JSON file")
    parser.add_argument("left_month", help="Month name for the left side")
    parser.add_argument("right_month", help="Month name for the right side")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CSV to JSON conversion CLI."""

    args = parse_args(sys.argv[1:] if argv is None else argv)
    convert_csv_to_json(args.input_csv, args.output_json, args.left_month, args.right_month)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())