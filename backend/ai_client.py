"""Unified AI client supporting Google Gemini, OpenAI, Anthropic, and OpenRouter.

Design contract (see CLAUDE.md): every provider returns an ``AIResponse`` whose
``.text`` is a plain string, so the regex-based JSON extraction downstream keeps
working regardless of which provider generated the response.
"""

import copy
import json
import logging

logger = logging.getLogger(__name__)

# Default models: the newest *low-cost* tier for each provider.
# Verified August 2026 — see README for the full table and pricing.
DEFAULT_MODELS: dict[str, str] = {
    "google": "gemini-3.6-flash",
    "openai": "gpt-5.6-luna",
    "anthropic": "claude-haiku-4-5",
    "openrouter": "openai/gpt-5.6-luna",
}

PROVIDERS = ("google", "openai", "anthropic", "openrouter")

# Evaluator responses carry 8-9 scored categories, each with justification,
# recommendation and error arrays. 4096 truncated them regularly, which produced
# unterminated JSON and a downstream parse failure.
MAX_OUTPUT_TOKENS = 16000


class AIError(RuntimeError):
    """Raised when a provider returns no usable text (refusal, safety block,
    truncation, or an empty candidate list)."""


class AIResponse:
    """Normalised response object — exposes a .text attribute so existing
    response-parsing helpers (regex JSON extraction etc.) continue to work
    unchanged regardless of which provider generated the response."""

    def __init__(self, text: str):
        self.text = text


def _require_text(text: str | None, provider: str, reason: str = "") -> str:
    """Guard the one failure mode every provider shares: a successful HTTP call
    that carries no usable text."""
    if not text or not text.strip():
        detail = f" ({reason})" if reason else ""
        raise AIError(
            f"The {provider} model returned no text{detail}. This usually means the "
            "response was blocked, refused, or truncated. Try again, or switch model."
        )
    return text.strip()


# Strict structured outputs (OpenAI and Anthropic) reject numeric and string
# constraints. Pydantic emits "minimum"/"maximum" for the rating field's ge/le,
# which would 400 the request, so they are stripped for those providers only —
# the 1-5 bound is restated in the prompt text instead.
_UNSUPPORTED_STRICT_KEYWORDS = frozenset({
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
    "minLength", "maxLength", "pattern", "minItems", "maxItems", "uniqueItems",
    "default", "examples",
})


def _strict_json_schema(schema):
    """Tighten a flattened Pydantic schema for OpenAI/Anthropic strict mode.

    Strict structured outputs require every object to set
    ``additionalProperties: false`` and to list *all* of its properties in
    ``required`` (our models have no optional fields, so this is a faithful
    tightening), and reject the validation keywords listed above.
    """
    if isinstance(schema, dict):
        node = {
            key: _strict_json_schema(value)
            for key, value in schema.items()
            if key not in _UNSUPPORTED_STRICT_KEYWORDS
        }
        if node.get("type") == "object" and "properties" in node:
            node["additionalProperties"] = False
            node["required"] = list(node["properties"].keys())
        return node
    if isinstance(schema, list):
        return [_strict_json_schema(item) for item in schema]
    return copy.deepcopy(schema)


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
    # Provider-specific text extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _google_json_config(system: str, schema: dict):
        """Build a JSON-mode config, preferring the raw-JSON-Schema parameter.

        ``response_json_schema`` is the correct home for a JSON Schema dict;
        ``response_schema`` expects the narrower OpenAPI subset. Older
        google-genai releases only have the latter, so fall back to it.
        """
        from google.genai import types  # type: ignore[import]

        common = dict(
            system_instruction=system,
            response_mime_type="application/json",
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )
        try:
            return types.GenerateContentConfig(response_json_schema=schema, **common)
        except (TypeError, ValueError) as exc:
            logger.warning(
                "google-genai rejected response_json_schema (%s); "
                "falling back to response_schema.", exc
            )
            return types.GenerateContentConfig(response_schema=schema, **common)

    @staticmethod
    def _google_text(resp) -> str:
        """``GenerateContentResponse.text`` is None (not "") when the response
        has no text parts — a safety block, or MAX_TOKENS consumed by thinking.
        Calling .strip() on that raised AttributeError."""
        text = getattr(resp, "text", None)
        if text:
            return text.strip()

        reason = ""
        candidates = getattr(resp, "candidates", None) or []
        if candidates:
            reason = str(getattr(candidates[0], "finish_reason", "") or "")
        elif getattr(resp, "prompt_feedback", None):
            reason = f"prompt blocked: {resp.prompt_feedback}"
        return _require_text(None, "Google", reason)

    @staticmethod
    def _anthropic_text(message) -> str:
        """Concatenate every text block.

        ``content[0].text`` broke in two ways: a refusal returns an empty
        ``content`` list (IndexError), and models with adaptive thinking enabled
        put a ``thinking`` block first (AttributeError).
        """
        if getattr(message, "stop_reason", None) == "refusal":
            details = getattr(message, "stop_details", None)
            category = getattr(details, "category", None) if details else None
            raise AIError(
                "The Anthropic model declined this request"
                f"{f' (category: {category})' if category else ''}."
            )

        parts = [
            block.text
            for block in (getattr(message, "content", None) or [])
            if getattr(block, "type", None) == "text" and getattr(block, "text", None)
        ]
        reason = ""
        if getattr(message, "stop_reason", None) == "max_tokens":
            reason = "hit max_tokens — the response was cut off"
        return _require_text("".join(parts), "Anthropic", reason)

    @staticmethod
    def _openai_text(completion, provider_label: str) -> str:
        choices = getattr(completion, "choices", None) or []
        if not choices:
            return _require_text(None, provider_label, "no choices returned")

        message = choices[0].message
        if getattr(message, "refusal", None):
            raise AIError(f"The {provider_label} model refused: {message.refusal}")

        reason = ""
        if getattr(choices[0], "finish_reason", None) == "length":
            reason = "hit the output token limit — the response was cut off"
        return _require_text(message.content, provider_label, reason)

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
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                ),
                contents=content,
            )
            return AIResponse(self._google_text(resp))

        elif self.provider in ("openai", "openrouter"):
            # OpenAI deprecated max_tokens in favour of max_completion_tokens and
            # current reasoning models reject the old name; OpenRouter normalises
            # on max_tokens for the many non-OpenAI models it proxies.
            limit = (
                {"max_completion_tokens": MAX_OUTPUT_TOKENS}
                if self.provider == "openai"
                else {"max_tokens": MAX_OUTPUT_TOKENS}
            )
            completion = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": content},
                ],
                **limit,
            )
            return AIResponse(self._openai_text(completion, self.provider))

        elif self.provider == "anthropic":
            message = self._client.messages.create(
                model=self.model,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=system,
                messages=[{"role": "user", "content": content}],
            )
            return AIResponse(self._anthropic_text(message))

        raise RuntimeError(f"Unhandled provider: {self.provider}")

    def generate_json(self, system: str, content: str, schema: dict) -> AIResponse:
        """Generate a JSON response conforming to the given schema.

        Google and OpenAI enforce the schema natively. Anthropic enforces it
        natively on models that support structured outputs and falls back to
        embedding the schema in the system prompt otherwise; OpenRouter uses
        JSON mode plus an embedded schema, because schema enforcement varies by
        the upstream model it routes to.

        All responses are returned as raw text so the existing regex-based JSON
        extraction helpers work without modification.
        """
        if self.provider == "google":
            resp = self._client.models.generate_content(
                model=self.model,
                config=self._google_json_config(system, schema),
                contents=content,
            )
            return AIResponse(self._google_text(resp))

        elif self.provider == "openai":
            try:
                completion = self._client.chat.completions.create(
                    model=self.model,
                    max_completion_tokens=MAX_OUTPUT_TOKENS,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": content},
                    ],
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "tef_evaluation",
                            "strict": True,
                            "schema": _strict_json_schema(schema),
                        },
                    },
                )
            except Exception as exc:  # noqa: BLE001 — schema mode is best-effort
                logger.warning(
                    "OpenAI strict schema mode failed (%s); falling back to JSON mode.", exc
                )
                completion = self._client.chat.completions.create(
                    model=self.model,
                    max_completion_tokens=MAX_OUTPUT_TOKENS,
                    messages=[
                        {"role": "system", "content": system + _schema_note(schema)},
                        {"role": "user", "content": content},
                    ],
                    response_format={"type": "json_object"},
                )
            return AIResponse(self._openai_text(completion, "openai"))

        elif self.provider == "openrouter":
            # OpenRouter proxies many upstream models; several silently ignore
            # response_format, so the embedded schema stays as a safety net.
            completion = self._client.chat.completions.create(
                model=self.model,
                max_tokens=MAX_OUTPUT_TOKENS,
                messages=[
                    {"role": "system", "content": system + _schema_note(schema)},
                    {"role": "user", "content": content},
                ],
                response_format={"type": "json_object"},
            )
            return AIResponse(self._openai_text(completion, "openrouter"))

        elif self.provider == "anthropic":
            try:
                message = self._client.messages.create(
                    model=self.model,
                    max_tokens=MAX_OUTPUT_TOKENS,
                    system=system,
                    messages=[{"role": "user", "content": content}],
                    output_config={
                        "format": {
                            "type": "json_schema",
                            "schema": _strict_json_schema(schema),
                        }
                    },
                )
            except Exception as exc:  # noqa: BLE001 — older models lack structured outputs
                logger.warning(
                    "Anthropic structured outputs unavailable (%s); "
                    "falling back to schema-in-prompt.", exc
                )
                message = self._client.messages.create(
                    model=self.model,
                    max_tokens=MAX_OUTPUT_TOKENS,
                    system=system + _schema_note(schema),
                    messages=[{"role": "user", "content": content}],
                )
            return AIResponse(self._anthropic_text(message))

        raise RuntimeError(f"Unhandled provider: {self.provider}")


def _schema_note(schema: dict) -> str:
    return (
        "\n\nYou MUST respond with valid JSON that exactly matches "
        f"this schema:\n{json.dumps(schema, indent=2)}"
    )
