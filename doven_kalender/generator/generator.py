"""LLM abstraction and generation helpers for doven-kalender.

This module centralizes all LLM provider integrations so both parser and generator
code paths can share the same interface.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
import os
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

TModel = TypeVar("TModel", bound=BaseModel)


class LLMError(RuntimeError):
    """Raised when an LLM provider fails to produce valid output."""


class GeneralLLM(ABC):
    """Abstract interface for plain-text and structured LLM generation.

    Implementations provide provider-specific calls in `_generate_text`, while
    this base class handles optional Pydantic validation for structured outputs.
    """

    @abstractmethod
    def _generate_text(self, query: str) -> str:
        """Return the provider response as text for a single query."""

    def generate(self, query: str, response_model: type[TModel] | None = None) -> str | TModel:
        if response_model is None:
            return self._generate_text(query)

        prompt = self._structured_prompt(query, response_model)
        raw_output = self._generate_text(prompt)

        try:
            raw_json: Any = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise LLMError("LLM did not return valid JSON for structured output.") from exc

        try:
            return response_model.model_validate(raw_json)
        except ValidationError as exc:
            raise LLMError("LLM JSON did not match the requested Pydantic schema.") from exc

    @staticmethod
    def _structured_prompt(query: str, response_model: type[BaseModel]) -> str:
        schema = json.dumps(response_model.model_json_schema(), ensure_ascii=False, indent=2)
        return (
            "You must answer as valid JSON matching this schema exactly. "
            "Do not include markdown fences or extra text.\n\n"
            f"Schema:\n{schema}\n\n"
            f"Task:\n{query}"
        )


class GeminiLLM(GeneralLLM):
    """Gemini implementation of the GeneralLLM interface."""

    def __init__(self, model: str = "gemini-2.5-flash", temperature: float | None = None):
        try:
            from google import genai
        except ImportError as exc:
            raise ImportError("google-genai is required for GeminiLLM.") from exc

        google_api_key = os.getenv("GEMINI_KEY")
        self._client = genai.Client(api_key=google_api_key)
        self._model = model
        self._temperature = temperature

    def _generate_text(self, query: str) -> str:
        config = {"temperature": self._temperature} if self._temperature is not None else None
        response = self._client.models.generate_content(
            model=self._model,
            contents=query,
            config=config,
        )
        return response.text or ""


class MistralLLM(GeneralLLM):
    def __init__(self, model: str = "mistral-small-latest", temperature: float | None = None):
        try:
            from mistralai import Mistral
        except ImportError as exc:
            raise ImportError("mistralai is required for MistralLLM.") from exc

        mistral_api_key = os.getenv("MISTRAL_KEY")
        self._client = Mistral(api_key=mistral_api_key)
        self._model = model
        self._temperature = temperature

    def _generate_text(self, query: str) -> str:
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": [{"role": "user", "content": query}],
        }
        if self._temperature is not None:
            kwargs["temperature"] = self._temperature

        response = self._client.chat.complete(**kwargs)
        return response.choices[0].message.content or ""


def create_llm(provider: str, model: str | None = None, temperature: float | None = None) -> GeneralLLM:
    normalized = provider.strip().lower()

    if normalized == "gemini":
        return GeminiLLM(model=model or "gemini-2.5-flash", temperature=temperature)
    if normalized == "mistral":
        return MistralLLM(model=model or "mistral-small-latest", temperature=temperature)

    raise ValueError(f"Unsupported LLM provider: {provider}")


class Generator:
    def __init__(
        self,
        llm: GeneralLLM | None = None,
        provider: str = "gemini",
        model: str | None = None,
    ):
        self._llm = llm or create_llm(provider=provider, model=model)

    def generate(self, query: str, response_model: type[TModel] | None = None) -> str | TModel:
        return self._llm.generate(query=query, response_model=response_model)
