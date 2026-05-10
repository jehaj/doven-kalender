"""Parser abstractions for transforming extracted events into typed data."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from ..generator.generator import GeneralLLM


class ParsedEvent(BaseModel):
    title: str = Field(description="Event title")
    description: str = Field(description="Event description")
    start_time: str = Field(description="Start timestamp in ISO-8601 format")
    end_time: str = Field(description="End timestamp in ISO-8601 format")


class EventParser:
    def __init__(self, llm: GeneralLLM):
        self._llm = llm

    def parse_event(self, event: dict[str, Any], response_model: type[BaseModel] = ParsedEvent) -> BaseModel:
        prompt = (
            "Parse this calendar event into structured data with normalized title, "
            "description, and ISO timestamps:\n"
            f"{event}"
        )
        return self._llm.generate(prompt, response_model=response_model)
