import json
import unittest
from unittest.mock import Mock, patch

import requests
from requests.exceptions import HTTPError, JSONDecodeError

from doven_kalender.extractor.kalender import get_events

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object  # type: ignore[assignment]
    HAS_PYDANTIC = False
else:
    HAS_PYDANTIC = True

if HAS_PYDANTIC:
    from doven_kalender import generate_description
    from doven_kalender.generator.generator import GeneralLLM, Generator, LLMError
    from doven_kalender.parser.parser import EventParser, ParsedEvent

# A sample successful response from the Google Calendar API
DUMMY_SUCCESS_RESPONSE = json.loads(r"""{
	"kind": "calendar#events",
	"etag": "\"p32nsda4rvm5os0o\"",
	"summary": "Åbyhøj IMU",
	"description": "",
	"updated": "2025-06-25T06:48:00.260Z",
	"timeZone": "Europe/Copenhagen",
	"accessRole": "reader",
	"defaultReminders": [],
	"nextSyncToken": "CK_GqJv9i44DEAAYASCC6cHxAiiC6cHxAg==",
	"items": [
		{
			"kind": "calendar#event",
			"etag": "\"3500387681181886\"",
			"id": "24qogpvq8p0euh5pugaau41jgg",
			"status": "confirmed",
			"htmlLink": "https://www.google.com/calendar/event?eid=MjRxb2dwdnE4cDBldWg1cHVnYWF1NDFqZ2cgZmo4OGU0NWZ2dWoyaGZobDNuMWcwbWxrdXNAZw&ctz=Europe/Copenhagen",
			"created": "2025-01-24T13:38:01.000Z",
			"updated": "2025-06-17T20:57:20.590Z",
			"summary": "Sommerafslutning ",
			"description": "MØ: Daniella\nMU: Cecilie\nKA: Marcus\nFR: -\nPR: Hannah og Mie",
			"creator": {
				"email": "mathiaswiwe@gmail.com"
			},
			"organizer": {
				"email": "fj88e45fvuj2hfhl3n1g0mlkus@group.calendar.google.com",
				"displayName": "Åbyhøj IMU",
				"self": true
			},
			"start": {
				"dateTime": "2025-06-19T19:00:00+02:00",
				"timeZone": "Europe/Brussels"
			},
			"end": {
				"dateTime": "2025-06-19T21:00:00+02:00",
				"timeZone": "Europe/Brussels"
			},
			"iCalUID": "24qogpvq8p0euh5pugaau41jgg@google.com",
			"sequence": 0,
			"eventType": "default"
		}
	]
}""")


class TestKalender(unittest.TestCase):
    @patch("doven_kalender.extractor.kalender.requests.get")
    def test_get_events_success(self, mock_get):
        """Test get_events successfully retrieves and parses events."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = DUMMY_SUCCESS_RESPONSE
        mock_get.return_value = mock_response

        calendar_id = "test_calendar"
        api_key = "test_api_key"
        events = get_events(calendar_id, api_key)

        self.assertEqual(mock_get.call_count, 1)
        self.assertEqual(events, DUMMY_SUCCESS_RESPONSE["items"])

        # Check if the URL and params were constructed correctly
        called_url = mock_get.call_args[0][0]
        self.assertIn(calendar_id, called_url)
        called_params = mock_get.call_args[1]["params"]
        self.assertEqual(called_params["key"], api_key)
        self.assertIn("timeMin", called_params)
        self.assertIn("timeMax", called_params)

    @patch("doven_kalender.extractor.kalender.requests.get")
    def test_get_events_http_error(self, mock_get):
        """Test get_events raises HTTPError on non-200 status."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("403 Client Error")
        mock_get.return_value = mock_response

        with self.assertRaises(HTTPError):
            get_events("test_calendar", "test_api_key")

    @patch("doven_kalender.extractor.kalender.requests.get")
    def test_get_events_network_error(self, mock_get):
        """Test get_events raises RequestException on network failure."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network is down")

        with self.assertRaises(requests.exceptions.ConnectionError):
            get_events("test_calendar", "test_api_key")

    @patch("doven_kalender.extractor.kalender.requests.get")
    def test_get_events_json_decode_error(self, mock_get):
        """Test get_events raises JSONDecodeError on invalid JSON response."""
        mock_response = Mock()
        mock_response.json.side_effect = JSONDecodeError("err", "doc", 0)
        mock_get.return_value = mock_response

        with self.assertRaises(JSONDecodeError):
            get_events("test_calendar", "test_api_key")


if HAS_PYDANTIC:
    class TestLLMAbstraction(unittest.TestCase):
        class _FakeLLM(GeneralLLM):
            """Test double for GeneralLLM that returns deterministic responses."""

            def __init__(self, response: str):
                self._response = response
                self.last_query = ""

            def _generate_text(self, query: str) -> str:
                self.last_query = query
                return self._response

        class _StructuredResponse(BaseModel):
            """Structured model used to validate pydantic parsing in tests."""

            value: str

        def test_generate_returns_text_without_response_model(self):
            """GeneralLLM.generate should return plain text when no model is requested."""
            llm = self._FakeLLM("hello")
            result = llm.generate("say hi")
            self.assertEqual(result, "hello")

        def test_generate_returns_pydantic_model_with_response_model(self):
            """GeneralLLM.generate should parse and validate JSON into a Pydantic model."""
            llm = self._FakeLLM('{"value": "ok"}')
            result = llm.generate("structured", response_model=self._StructuredResponse)
            self.assertEqual(result.value, "ok")

        def test_generate_raises_on_invalid_json(self):
            """GeneralLLM.generate should raise LLMError when JSON decoding fails."""
            llm = self._FakeLLM("not-json")
            with self.assertRaises(LLMError):
                llm.generate("structured", response_model=self._StructuredResponse)


    class TestParserAndGeneratorWiring(unittest.TestCase):
        class _FakeLLM(GeneralLLM):
            """Test double for parser/generator wiring tests."""

            def __init__(self, response: str):
                self._response = response
                self.last_query = ""

            def _generate_text(self, query: str) -> str:
                self.last_query = query
                return self._response

        def test_event_parser_uses_structured_output(self):
            """EventParser should ask the shared LLM for structured output."""
            llm = self._FakeLLM(
                '{"title": "IMU", "description": "Aften", '
                '"start_time": "2026-04-27T19:00:00+02:00", '
                '"end_time": "2026-04-27T21:00:00+02:00"}'
            )
            parser = EventParser(llm)
            event = {
                "summary": "IMU",
                "description": "Aften",
                "start": {"dateTime": "2026-04-27T19:00:00+02:00"},
                "end": {"dateTime": "2026-04-27T21:00:00+02:00"},
            }

            parsed = parser.parse_event(event)

            self.assertIsInstance(parsed, ParsedEvent)
            self.assertIn("Parse this calendar event", llm.last_query)

        @patch("doven_kalender.create_llm")
        def test_generate_description_uses_shared_llm_generator(self, mock_create_llm):
            """generate_description should use Generator with a shared LLM instance."""
            fake_llm = self._FakeLLM("Generated post")
            mock_create_llm.return_value = fake_llm

            event = ParsedEvent(
                title="IMU",
                description="Aften i kirken",
                start_time="2026-04-27T19:00:00+02:00",
                end_time="2026-04-27T21:00:00+02:00",
            )

            text = generate_description(event, provider="openai")

            self.assertEqual(text, "Generated post")
            self.assertIn("Facebook announcement", fake_llm.last_query)

        def test_generator_wrapper_delegates_to_shared_llm(self):
            """Generator wrapper should delegate generation calls to the shared LLM."""
            llm = self._FakeLLM("wrapped")
            generator = Generator(llm)

            result = generator.generate("prompt")

            self.assertEqual(result, "wrapped")
            self.assertEqual(llm.last_query, "prompt")


if __name__ == "__main__":
    unittest.main()
