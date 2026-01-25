from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


class GeminiError(RuntimeError):
    pass


@dataclass(frozen=True)
class GeminiConfig:
    api_key: str
    model: str = "gemini-1.5-flash"
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    timeout_s: float = 20.0
    temperature: float = 0.4
    max_output_tokens: int = 800


def load_gemini_config_from_env() -> GeminiConfig:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise GeminiError("GEMINI_API_KEY is not set")

    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip() or "gemini-1.5-flash"
    base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta").strip()

    # Keep parsing conservative; these are optional knobs for local tuning.
    def _float(name: str, default: float) -> float:
        val = os.getenv(name)
        if val is None or val.strip() == "":
            return default
        try:
            return float(val)
        except ValueError as e:
            raise GeminiError(f"Invalid {name}={val!r}") from e

    def _int(name: str, default: int) -> int:
        val = os.getenv(name)
        if val is None or val.strip() == "":
            return default
        try:
            return int(val)
        except ValueError as e:
            raise GeminiError(f"Invalid {name}={val!r}") from e

    return GeminiConfig(
        api_key=api_key,
        model=model,
        base_url=base_url,
        timeout_s=_float("GEMINI_TIMEOUT_S", 20.0),
        temperature=_float("GEMINI_TEMPERATURE", 0.4),
        max_output_tokens=_int("GEMINI_MAX_OUTPUT_TOKENS", 800),
    )


def generate_text(prompt: str, *, cfg: GeminiConfig) -> str:
    """
    Calls Gemini (Generative Language API) and returns the model's plain text.
    """
    url = f"{cfg.base_url}/models/{cfg.model}:generateContent"
    params = {"key": cfg.api_key}

    body: dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": cfg.temperature,
            "maxOutputTokens": cfg.max_output_tokens,
        },
    }

    try:
        resp = requests.post(url, params=params, json=body, timeout=cfg.timeout_s)
    except requests.RequestException as e:
        raise GeminiError(f"Gemini request failed: {e}") from e

    if resp.status_code >= 400:
        raise GeminiError(f"Gemini HTTP {resp.status_code}: {resp.text[:500]}")

    try:
        data = resp.json()
    except ValueError as e:
        raise GeminiError(f"Gemini returned non-JSON response: {resp.text[:500]}") from e

    # Expected shape: candidates[0].content.parts[0].text
    try:
        candidates = data.get("candidates") or []
        content = candidates[0].get("content") or {}
        parts = content.get("parts") or []
        text = parts[0].get("text")
    except Exception as e:
        raise GeminiError(f"Unexpected Gemini response shape: {str(data)[:500]}") from e

    if not isinstance(text, str) or not text.strip():
        raise GeminiError("Gemini returned empty text")

    return text

