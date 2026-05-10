"""Application orchestration for doven-kalender.

Flow: extractor -> parser -> integrator/generator.
"""

from __future__ import annotations

import os
import sys
from typing import Any

from .generator.generator import Generator, create_llm
from .extractor.kalender import JSONType, get_events
from .parser.parser import EventParser, ParsedEvent


def parse_event_with_llm(event: JSONType, provider: str = "openai") -> ParsedEvent:
    if not isinstance(event, dict):
        raise TypeError("Expected event to be a dictionary-like object.")

    llm = create_llm(provider)
    parser = EventParser(llm)
    return parser.parse_event(event, response_model=ParsedEvent)


def generate_description(event: ParsedEvent, provider: str = "openai") -> str:
    llm = create_llm(provider)
    generator = Generator(llm)
    prompt = (
        "Write a concise and warm Facebook announcement in Danish based on this "
        "event information:\n"
        f"Title: {event.title}\n"
        f"Description: {event.description}\n"
        f"Start: {event.start_time}\n"
        f"End: {event.end_time}"
    )
    output = generator.generate(prompt)
    if not isinstance(output, str):
        raise TypeError("Expected text output from generator.")
    return output


def weekday_name(weekday_index: int) -> str:
    names = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
    return names[weekday_index]


def main() -> int:
    print("Doven Kalender")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.", file=sys.stderr)
        return 1

    provider = os.getenv("DOVEN_LLM_PROVIDER", "openai")
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "fj88e45fvuj2hfhl3n1g0mlkus")
    events = get_events(calendar_id, api_key)
    if not events:
        print("Der er ingen begivenheder i den kommende uge.")
        return 0

    parsed_event = parse_event_with_llm(events[0], provider=provider)
    post_description = generate_description(parsed_event, provider=provider)
    print(post_description)
    return 0


__all__ = ["main", "parse_event_with_llm", "generate_description", "weekday_name"]
