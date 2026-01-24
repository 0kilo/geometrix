"""LiteLLM wrapper for structured LaTeX JSON responses."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

SUPPORTED_PROVIDERS = {"anthropic", "openai", "qwen", "xai", "gemini", "deepseek"}

PROVIDER_ENV_KEYS: dict[str, tuple[str, ...]] = {
    "openai": ("OPENAI_API_KEY",),
    "anthropic": ("ANTHROPIC_API_KEY",),
    "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "xai": ("XAI_API_KEY",),
    "qwen": ("QWEN_API_KEY", "DASHSCOPE_API_KEY"),
    "deepseek": ("DEEPSEEK_API_KEY",),
}


@dataclass(frozen=True)
class LLMConfig:
    """Configuration for LiteLLM calls."""

    provider: str
    model: str
    api_key: str | None = None
    base_url: str | None = None
    timeout_s: float | None = 30.0

    @property
    def model_id(self) -> str:
        if "/" in self.model:
            return self.model
        return f"{self.provider}/{self.model}"


def request_llm_json(
    config: LLMConfig,
    system_prompt: str,
    user_prompt: str,
    *,
    enforce_json: bool = True,
    max_retries: int = 0,
    extra_params: dict[str, Any] | None = None,
) -> str:
    """Send a JSON-only request via LiteLLM and return the model response text."""

    provider = config.provider.strip().lower()
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported provider: {config.provider}")

    api_key = config.api_key or _resolve_api_key(provider)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    payload: dict[str, Any] = {
        "model": config.model_id,
        "messages": messages,
        "timeout": config.timeout_s,
    }
    if api_key:
        payload["api_key"] = api_key
    if config.base_url:
        payload["base_url"] = config.base_url
    if enforce_json and provider in {"openai", "xai"}:
        payload["response_format"] = {"type": "json_object"}
    if extra_params:
        payload.update(extra_params)

    try:
        from litellm import completion
    except ImportError as exc:
        raise RuntimeError(
            "litellm is required for LLM requests. Install with `pip install litellm`."
        ) from exc

    last_error: Exception | None = None
    for _ in range(max_retries + 1):
        try:
            response = completion(**payload)
            print(response)
            return _extract_content(response)
        except Exception as exc:
            last_error = exc
    raise RuntimeError("LiteLLM request failed after retries") from last_error


def _resolve_api_key(provider: str) -> str | None:
    for env_key in PROVIDER_ENV_KEYS.get(provider, ()):
        value = os.environ.get(env_key)
        if value:
            return value
    return None


def _extract_content(response: Any) -> str:
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        try:
            choices = response.choices
            return choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            raise ValueError("Unexpected LiteLLM response structure") from exc
