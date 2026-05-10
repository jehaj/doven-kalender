"""LLM abstraction and generation helpers for doven-kalender.

This module centralizes all LLM provider integrations so both parser and generator
code paths can share the same interface.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
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
        """Generate plain text or a Pydantic-validated structured response.

        Args:
            query: User query or prompt text.
            response_model: Optional Pydantic model used for structured output.

        Returns:
            Raw text when `response_model` is None, otherwise an instance of
            the provided model.

        Raises:
            LLMError: If JSON cannot be parsed or validation fails.
        """
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
        """Build a strict JSON-only prompt using a Pydantic JSON schema."""
        schema = json.dumps(response_model.model_json_schema(), ensure_ascii=False, indent=2)
        return (
            "You must answer as valid JSON matching this schema exactly. "
            "Do not include markdown fences or extra text.\n\n"
            f"Schema:\n{schema}\n\n"
            f"Task:\n{query}"
        )


class GoogleLLM(GeneralLLM):
    """Google Gemini implementation of the GeneralLLM interface."""

    def __init__(self, model: str = "gemini-2.5-flash"):
        """Initialize the Google client.

        Args:
            model: Gemini model identifier.

        Raises:
            ImportError: If the google-genai package is not installed.
        """
        try:
            from google import genai
        except ImportError as exc:
            raise ImportError("google-genai is required for GoogleLLM.") from exc

        self._client = genai.Client()
        self._model = model

    def _generate_text(self, query: str) -> str:
        """Generate text from Gemini for the supplied query."""
        response = self._client.models.generate_content(model=self._model, contents=query)
        return response.text or ""


class OpenAILLM(GeneralLLM):
    """OpenAI implementation of the GeneralLLM interface."""

    def __init__(self, model: str = "gpt-4o"):
        """Initialize the OpenAI client.

        Args:
            model: OpenAI model identifier.

        Raises:
            ImportError: If the openai package is not installed.
        """
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("openai is required for OpenAILLM.") from exc

        self._client = OpenAI()
        self._model = model

    def _generate_text(self, query: str) -> str:
        """Generate text from OpenAI chat completions for the supplied query."""
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": query}],
        )
        return response.choices[0].message.content or ""


class MistralLLM(GeneralLLM):
    """Mistral implementation of the GeneralLLM interface."""

    def __init__(self, model: str = "mistral-small-latest"):
        """Initialize the Mistral client.

        Args:
            model: Mistral model identifier.

        Raises:
            ImportError: If the mistralai package is not installed.
        """
        try:
            from mistralai import Mistral
        except ImportError as exc:
            raise ImportError("mistralai is required for MistralLLM.") from exc

        self._client = Mistral()
        self._model = model

    def _generate_text(self, query: str) -> str:
        """Generate text from Mistral chat completions for the supplied query."""
        response = self._client.chat.complete(
            model=self._model,
            messages=[{"role": "user", "content": query}],
        )
        return response.choices[0].message.content or ""


def create_llm(provider: str, model: str | None = None) -> GeneralLLM:
    """Create a concrete LLM implementation by provider name.

    Args:
        provider: One of "google", "openai", or "mistral".
        model: Optional provider model name override.

    Returns:
        A concrete `GeneralLLM` implementation.

    Raises:
        ValueError: If provider is unknown.
    """
    normalized = provider.strip().lower()

    if normalized == "google":
        return GoogleLLM(model=model or "gemini-2.5-flash")
    if normalized == "openai":
        return OpenAILLM(model=model or "gpt-4o")
    if normalized == "mistral":
        return MistralLLM(model=model or "mistral-small-latest")

    raise ValueError(f"Unsupported LLM provider: {provider}")


class Generator:
    """High-level generator using the shared LLM interface.

    This keeps generation logic provider-agnostic by delegating to `GeneralLLM`.
    """

    def __init__(
        self,
        llm: GeneralLLM | None = None,
        provider: str = "openai",
        model: str | None = None,
    ):
        """Initialize the generator with a concrete or provider-built LLM.

        Args:
            llm: Optional prebuilt LLM implementation for dependency injection.
            provider: Provider name used when `llm` is not supplied.
            model: Optional provider model override.
        """
        self._llm = llm or create_llm(provider=provider, model=model)

    def generate(self, query: str, response_model: type[TModel] | None = None) -> str | TModel:
        """Generate either free-form text or a structured Pydantic object."""
        return self._llm.generate(query=query, response_model=response_model)
