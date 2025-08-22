import json
import unittest
from unittest.mock import Mock, patch

import requests
from requests.exceptions import HTTPError, JSONDecodeError

from kalender import get_events

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
    @patch("kalender.requests.get")
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

    @patch("kalender.requests.get")
    def test_get_events_http_error(self, mock_get):
        """Test get_events raises HTTPError on non-200 status."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("403 Client Error")
        mock_get.return_value = mock_response

        with self.assertRaises(HTTPError):
            get_events("test_calendar", "test_api_key")

    @patch("kalender.requests.get")
    def test_get_events_network_error(self, mock_get):
        """Test get_events raises RequestException on network failure."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network is down")

        with self.assertRaises(requests.exceptions.ConnectionError):
            get_events("test_calendar", "test_api_key")

    @patch("kalender.requests.get")
    def test_get_events_json_decode_error(self, mock_get):
        """Test get_events raises JSONDecodeError on invalid JSON response."""
        mock_response = Mock()
        mock_response.json.side_effect = JSONDecodeError("err", "doc", 0)
        mock_get.return_value = mock_response

        with self.assertRaises(JSONDecodeError):
            get_events("test_calendar", "test_api_key")


class GeneralTests(unittest.TestCase):
    def test_env_keys_exist_in_example(self):
        """Test that all keys in .env exist in .env.example"""
        try:
            env_keys = set()
            example_keys = set()

            with open(".env") as env_file, open(".env.example") as example_file:
                for line in env_file:
                    if "=" in line and not line.startswith("#"):
                        env_keys.add(line.split("=")[0].strip())

                for line in example_file:
                    if "=" in line and not line.startswith("#"):
                        example_keys.add(line.split("=")[0].strip())

            missing_keys = env_keys - example_keys

            self.assertEqual(
                missing_keys,
                set(),
                f"Keys in .env missing from .env.example: {missing_keys}",
            )
        except FileNotFoundError as e:
            self.fail(f"Could not find environment files: {e}")


class EnvironmentTests(unittest.TestCase):
    def test_load_dotenv(self):
        """Test that the .env file is loaded correctly."""
        from environment import load_dotenv, get_value

        load_dotenv()

        # Check if a known variable is set
        self.assertNotEqual("", get_value("GOOGLE_API_KEY"))

    def test_get_value(self):
        """Test that get_value retrieves the correct environment variable."""
        from environment import load_dotenv, get_value

        load_dotenv()

        # Assuming GOOGLE_API_KEY is set in the .env file
        api_key = get_value("GOOGLE_API_KEY")
        self.assertIsInstance(api_key, str)
        self.assertGreater(len(api_key), 0)

    def test_non_value(self):
        """Test that get_value fails for nonexisting environment variable."""
        from environment import load_dotenv, get_value

        load_dotenv()

        # Should throw ValueError since the key does not exist
        with self.assertRaises(ValueError):
            get_value("FAKE_API_KEY")

    def test_setting_value(self):
        """Test that get_value retrieves the correct environment variable
        after setting it."""
        from environment import load_dotenv, get_value

        load_dotenv()

        import os

        os.environ["GOOGLE_API_KEY"] = "TEST_VALUE"

        # Assuming GOOGLE_API_KEY is set in the .env file
        api_key = get_value("GOOGLE_API_KEY")
        self.assertIsInstance(api_key, str)
        self.assertEqual(api_key, "TEST_VALUE")


if __name__ == "__main__":
    unittest.main()
