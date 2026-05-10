import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from doven_kalender.parser.get_emojis import (
    add_emojis_to_json,
    assign_emojis_to_entries,
    build_emoji_prompt,
    load_env_file,
)


class _FakeLLM:
    def __init__(self, response_text: str):
        self.response_text = response_text
        self.calls: list[tuple[str, object | None]] = []

    def generate(self, query: str):
        self.calls.append((query, None))
        return self.response_text


class TestGetEmojis(unittest.TestCase):
    def test_load_env_file_parses_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text('MISTRAL_API_KEY="secret"\nGOOGLE_API_KEY=abc123\n', encoding="utf-8")

            os.environ.pop("MISTRAL_API_KEY", None)
            os.environ.pop("GOOGLE_API_KEY", None)

            loaded = load_env_file(env_path)

            self.assertTrue(loaded)
            self.assertEqual(os.environ["MISTRAL_API_KEY"], "secret")
            self.assertEqual(os.environ["GOOGLE_API_KEY"], "abc123")

    def test_build_emoji_prompt_includes_titles(self) -> None:
        prompt = build_emoji_prompt([
            {"title": "Sommerfest", "description": "Aften"},
            {"title": "Bøn", "description": ""},
        ])

        self.assertIn("Sommerfest", prompt)
        self.assertIn("Bøn", prompt)
        self.assertIn('{"emojis": ["😀", "🎉"]}', prompt)

    @patch("doven_kalender.parser.get_emojis.load_llm")
    def test_assign_emojis_to_entries_defaults_to_mistral(self, mock_load_llm) -> None:
        fake_llm = _FakeLLM('{"emojis": ["🎉", "🙏"]}')
        mock_load_llm.return_value = fake_llm

        result = assign_emojis_to_entries(
            [{"title": "Sommerfest", "description": "Aften"}, {"title": "Bøn", "description": ""}],
        )

        self.assertEqual(result[0]["emoji"], "🎉")
        self.assertEqual(result[1]["emoji"], "🙏")
        mock_load_llm.assert_called_once()
        self.assertEqual(mock_load_llm.call_args.kwargs["provider"], "mistral")
        self.assertIs(mock_load_llm.call_args.kwargs["env_file"], None)
        self.assertIsNone(fake_llm.calls[0][1])

    @patch("doven_kalender.parser.get_emojis.load_llm")
    def test_add_emojis_to_json_writes_updated_file(self, mock_load_llm) -> None:
        fake_llm = _FakeLLM('{"emojis": ["🎉"]}')
        mock_load_llm.return_value = fake_llm

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "input.json"
            output_path = temp_path / "output.json"
            input_path.write_text(
                json.dumps({"left": [{"title": "Sommerfest", "description": "Aften", "emoji": None}], "right": []}),
                encoding="utf-8",
            )

            updated = add_emojis_to_json(input_path, output_path, provider="google")

            self.assertEqual(updated["left"][0]["emoji"], "🎉")
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(written["left"][0]["emoji"], "🎉")
            self.assertEqual(mock_load_llm.call_args.kwargs["provider"], "google")