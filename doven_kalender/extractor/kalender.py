import json
import os
import sys
import typing
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from requests.exceptions import HTTPError, JSONDecodeError

JSONType = typing.Union[
    dict[str, "JSONType"], list["JSONType"], str, int, float, bool, None
]

# Base URL for the Google Calendar API
API_BASE_URL = "https://clients6.google.com/calendar/v3/calendars"


def get_events(calendar_id: str, api_key: str) -> list[JSONType]:
    copenhagen_tz = ZoneInfo("Europe/Copenhagen")
    time_min = datetime.now(copenhagen_tz)
    time_max = time_min + timedelta(weeks=1)

    params: dict[str, str | int] = {
        "key": api_key,
        "singleEvents": "true",
        "timeZone": "Europe/Copenhagen",
        "maxResults": 10,
        "timeMin": time_min.isoformat(),
        "timeMax": time_max.isoformat(),
    }

    url = f"{API_BASE_URL}/{calendar_id}@group.calendar.google.com/events"

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("items", [])


def dummy_get_events(calendar_id: str) -> list[JSONType]:
    return []


if __name__ == "__main__":
    print("Trying to get next calendar event.")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    calendar_id = "fj88e45fvuj2hfhl3n1g0mlkus"
    try:
        events = get_events(calendar_id, api_key)
        if events:
            print(f"Found {len(events)} event(s).")
            print(json.dumps(events[0], indent=2, ensure_ascii=False))
        else:
            print("No upcoming events found in the next week.")
    except (HTTPError, JSONDecodeError, requests.exceptions.RequestException) as e:
        print(f"Error fetching calendar events: {e}", file=sys.stderr)
        sys.exit(1)
