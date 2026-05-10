"""Application orchestration for doven-kalender.

Flow: extractor -> parser -> integrator/generator.
"""

from __future__ import annotations

import os
import sys
from typing import Any

from generator.generator import Generator, create_llm
from extractor.kalender import JSONType, get_events
from parser.parser import EventParser, ParsedEvent


def parse_event_with_llm(event: JSONType, provider: str = "openai") -> ParsedEvent:
    """Parse a raw extracted event into a structured event model.

    Args:
        event: Event object from the extractor.
        provider: LLM provider name (google, openai, mistral).

    Returns:
        Structured event data validated by Pydantic.
    """
    if not isinstance(event, dict):
        raise TypeError("Expected event to be a dictionary-like object.")

    llm = create_llm(provider)
    parser = EventParser(llm)
    return parser.parse_event(event, response_model=ParsedEvent)


def generate_description(event: ParsedEvent, provider: str = "openai") -> str:
    """Generate a human-readable social post description from parsed event data.

    Args:
        event: Parsed event model.
        provider: LLM provider name (google, openai, mistral).

    Returns:
        Generated free-form post text.
    """
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
    """Return Danish weekday name from zero-based weekday index.

    Args:
        weekday_index: Integer weekday index where 0 is Monday.

    Returns:
        Danish weekday name.
    """
    names = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
    return names[weekday_index]


def main() -> int:
    """Run the end-to-end extraction -> parsing -> generation orchestration.

    Returns:
        Process exit code.
    """
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


if __name__ == "__main__":
    sys.exit(main())
