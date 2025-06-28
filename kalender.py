import typing
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import requests

JSONType = typing.Union[
    dict[str, "JSONType"], list["JSONType"], str, int, float, bool, None
]


def get_events(calendar_id: str) -> list[JSONType]:
    current_time = datetime.now(timezone(timedelta(hours=+2)))
    later = current_time + timedelta(weeks=1)
    time_min_encoded = encoded(current_time)
    time_max_encoded = encoded(later)
    query = f"https://clients6.google.com/calendar/v3/calendars/fj88e45fvuj2hfhl3n1g0mlkus%40group.calendar.google.com/events?calendarId={calendar_id}%40group.calendar.google.com&singleEvents=true&eventTypes=default&timeZone=Europe%2FCopenhagen&maxResults=10&sanitizeHtml=true&timeMin={time_min_encoded}&timeMax={time_max_encoded}&key=AIzaSyDOtGM5jr8bNp1utVpG2_gSRH03RNGBkI8&%24unique=gc456"
    response = requests.get(query)
    return response.json()["items"]


def dummy_get_events(calendar_id: str) -> list[JSONType]:
    """
    A dummy function that returns the same Google Calendar response
    with dict that always has events.

    :param calendar_id:
    :return: Google Calendar dict with events
    """
    import json

    return json.loads(r"""{
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
}""")["items"]


def encoded(value: datetime) -> str:
    formatted = value.strftime("%Y-%m-%dT00:00:00%:z")
    encoded_value = quote(formatted)
    return encoded_value


if __name__ == "__main__":
    print("Trying to get next calendar event.")
    calendar_id = "fj88e45fvuj2hfhl3n1g0mlkus"
    events = get_events(calendar_id)
    print(events)
