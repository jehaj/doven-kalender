"""Parser abstractions for transforming extracted events into typed data."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from generator import GeneralLLM


class ParsedEvent(BaseModel):
    """Structured event representation used by downstream generators/integrators."""

    title: str = Field(description="Event title")
    description: str = Field(description="Event description")
    start_time: str = Field(description="Start timestamp in ISO-8601 format")
    end_time: str = Field(description="End timestamp in ISO-8601 format")


class EventParser:
    """Parser service that uses a generic LLM to extract structured event fields."""

    def __init__(self, llm: GeneralLLM):
        """Initialize parser with the shared LLM interface.

        Args:
            llm: Concrete LLM implementation used for parsing.
        """
        self._llm = llm

    def parse_event(self, event: dict[str, Any], response_model: type[BaseModel] = ParsedEvent) -> BaseModel:
        """Parse an extracted event dict into a structured Pydantic model.

        Args:
            event: Raw event object from the extractor.
            response_model: Structured output schema. Defaults to `ParsedEvent`.

        Returns:
            Parsed event as the requested Pydantic model.
        """
        prompt = (
            "Parse this calendar event into structured data with normalized title, "
            "description, and ISO timestamps:\n"
            f"{event}"
        )
        return self._llm.generate(prompt, response_model=response_model)
