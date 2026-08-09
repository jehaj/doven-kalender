import csv
import json
import tempfile
import unittest
from pathlib import Path

from doven_kalender.parser.convert_csv_to_json import (
    classify_month,
    convert_csv_to_json,
    extract_date_parts,
    normalize_date,
    normalize_month_name,
)


class TestCsvToJsonConversion(unittest.TestCase):
    def test_extract_date_parts(self) -> None:
        self.assertEqual(extract_date_parts("8. juli"), (8, "juli"))

    def test_normalize_month_name(self) -> None:
        self.assertEqual(normalize_month_name("Juli"), "jul")
        self.assertEqual(normalize_month_name("august"), "aug")

    def test_normalize_date(self) -> None:
        self.assertEqual(normalize_date("8. juli"), "8. jul")
        self.assertEqual(normalize_date("4. august"), "4. aug")

    def test_classify_month(self) -> None:
        self.assertEqual(classify_month("jul", "jul", "aug"), "left")
        self.assertEqual(classify_month("aug", "jul", "aug"), "right")
        self.assertIsNone(classify_month("sep", "jul", "aug"))

    def test_convert_csv_to_json_routes_rows_by_target_month(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            csv_path = temp_path / "input.csv"
            json_path = temp_path / "output.json"

            with csv_path.open("w", newline="", encoding="utf-8") as csv_handle:
                writer = csv.writer(csv_handle)
                writer.writerow(["Dato", "Titel", "Emne/aktivitet"])
                writer.writerow(["8. juli", "abc", "def"])
                writer.writerow(["4. august", "ghi", ""])
                writer.writerow(["1. september", "skip me", "ignored"])

            convert_csv_to_json(csv_path, json_path, "juli", "august")

            with json_path.open(encoding="utf-8") as json_handle:
                result = json.load(json_handle)

            self.assertEqual(
                result,
                {
                    "months": "Juli & August",
                    "left_month": "Juli",
                    "right_month": "August",
                    "left": [
                        {
                            "date": "8. jul",
                            "emoji": None,
                            "title": "abc",
                            "description": "def",
                        }
                    ],
                    "right": [
                        {
                            "date": "4. aug",
                            "emoji": None,
                            "title": "ghi",
                            "description": "",
                        }
                    ],
                },
            )