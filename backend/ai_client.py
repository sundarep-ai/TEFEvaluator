"""Unified AI client supporting Google Gemini, OpenAI, Anthropic, and OpenRouter."""

import json

DEFAULT_MODELS: dict[str, str] = {
    "google": "gemini-2.5-pro",
    "openai": "gpt-4o",
    "anthropic": "claude-opus-4-6",
    "openrouter": "openai/gpt-4o",
}

PROVIDERS = ("google", "openai", "anthropic", "openrouter")


class AIResponse:
    """Normalised response object — exposes a .text attribute so existing
    response-parsing helpers (regex JSON extraction etc.) continue to work
    unchanged regardless of which provider generated the response."""

    def __init__(self, text: str):
        self.text = text


class UnifiedAIClient:
    def __init__(self, provider: str, api_key: str, model: str):
        if provider not in PROVIDERS:
            raise ValueError(
                f"Unknown provider '{provider}'. Choose from: {PROVIDERS}"
            )
        self.provider = provider
        self.model = model
        self._init_client(provider, api_key)

    # ------------------------------------------------------------------
    # Internal client construction
    # ------------------------------------------------------------------

    def _init_client(self, provider: str, api_key: str) -> None:
        if provider == "google":
            from google import genai  # type: ignore[import]
            self._client = genai.Client(api_key=api_key)

        elif provider == "openai":
            from openai import OpenAI
            self._client = OpenAI(api_key=api_key)

        elif provider == "anthropic":
            from anthropic import Anthropic
            self._client = Anthropic(api_key=api_key)

        elif provider == "openrouter":
            from openai import OpenAI
            self._client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
            )

    # ------------------------------------------------------------------
    # Public generation methods
    # ------------------------------------------------------------------

    def generate_text(self, system: str, content: str) -> AIResponse:
        """Generate a plain-text response."""
        if self.provider == "google":
            from google.genai import types  # type: ignore[import]
            resp = self._client.models.generate_content(
                model=self.model,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    response_mime_type="text/plain",
                ),
                contents=content,
            )
            return AIResponse(getattr(resp, "text", "").strip())

        elif self.provider in ("openai", "openrouter"):
            completion = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": content},
                ],
            )
            return AIResponse((completion.choices[0].message.content or "").strip())

        elif self.provider == "anthropic":
            message = self._client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system,
                messages=[{"role": "user", "content": content}],
            )
            return AIResponse(message.content[0].text.strip())

        raise RuntimeError(f"Unhandled provider: {self.provider}")

    def generate_json(self, system: str, content: str, schema: dict) -> AIResponse:
        """Generate a JSON response conforming to the given schema.

        Google uses native response_schema enforcement.
        OpenAI / OpenRouter use json_object mode with schema embedded in the
        system prompt.
        Anthropic embeds the schema in the system prompt (no native JSON mode).
        All responses are returned as raw text so existing regex-based JSON
        extraction helpers work without modification.
        """
        if self.provider == "google":
            from google.genai import types  # type: ignore[import]
            resp = self._client.models.generate_content(
                model=self.model,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
                contents=content,
            )
            return AIResponse(getattr(resp, "text", "").strip())

        elif self.provider in ("openai", "openrouter"):
            schema_note = (
                "\n\nYou MUST respond with valid JSON that exactly matches "
                f"this schema:\n{json.dumps(schema, indent=2)}"
            )
            completion = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system + schema_note},
                    {"role": "user", "content": content},
                ],
                response_format={"type": "json_object"},
            )
            return AIResponse((completion.choices[0].message.content or "").strip())

        elif self.provider == "anthropic":
            schema_note = (
                "\n\nYou MUST respond with valid JSON that exactly matches "
                f"this schema:\n{json.dumps(schema, indent=2)}"
            )
            message = self._client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system + schema_note,
                messages=[{"role": "user", "content": content}],
            )
            return AIResponse(message.content[0].text.strip())

        raise RuntimeError(f"Unhandled provider: {self.provider}")
