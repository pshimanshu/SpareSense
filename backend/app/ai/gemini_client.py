from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from typing import Any, Optional

import requests


class GeminiError(RuntimeError):
    pass


@dataclass(frozen=True)
class GeminiConfig:
    api_key: str
    # Prefer a stable, broadly available model name. (ListModels can confirm availability.)
    model: str = "gemini-2.0-flash"
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    timeout_s: float = 20.0
    temperature: float = 0.2
    # Default higher to avoid truncated JSON responses for structured outputs.
    max_output_tokens: int = 2048
    # Retry a small number of times on 429 rate limits (common on free tier).
    max_retries: int = 1
    max_retry_sleep_s: float = 10.0


def load_gemini_config_from_env() -> GeminiConfig:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise GeminiError("GEMINI_API_KEY is not set")

    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip() or "gemini-2.0-flash"
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
        temperature=_float("GEMINI_TEMPERATURE", 0.2),
        max_output_tokens=_int("GEMINI_MAX_OUTPUT_TOKENS", 2048),
        max_retries=_int("GEMINI_MAX_RETRIES", 1),
        max_retry_sleep_s=_float("GEMINI_MAX_RETRY_SLEEP_S", 10.0),
    )


_RETRY_IN_RE = re.compile(r"retry in\s+([0-9]+(?:\.[0-9]+)?)s", re.IGNORECASE)


def _compute_retry_sleep_s(resp: requests.Response) -> Optional[float]:
    """
    Derive a safe sleep duration for 429 responses.
    - Prefer Retry-After header if present.
    - Otherwise parse "Please retry in Xs" from the error message.
    """
    ra = resp.headers.get("retry-after")
    if ra:
        try:
            return float(ra)
        except ValueError:
            pass

    try:
        data = resp.json()
        msg = (((data.get("error") or {}).get("message")) or "")
    except ValueError:
        msg = resp.text or ""

    m = _RETRY_IN_RE.search(msg)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def generate_text(prompt: str, *, cfg: GeminiConfig) -> str:
    """
    Calls Gemini (Generative Language API) and returns the model's plain text.
    """
    model = cfg.model.strip()
    # Accept either "gemini-2.0-flash" or the fully qualified "models/gemini-2.0-flash".
    if not model.startswith("models/"):
        model = f"models/{model}"

    url = f"{cfg.base_url}/{model}:generateContent"
    params = {"key": cfg.api_key}

    body: dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": cfg.temperature,
            "maxOutputTokens": cfg.max_output_tokens,
            # Hint to Gemini that we want raw JSON (helps avoid markdown/code-fences).
            "responseMimeType": "application/json",
        },
    }

    attempt = 0
    while True:
        attempt += 1
        try:
            resp = requests.post(url, params=params, json=body, timeout=cfg.timeout_s)
        except requests.RequestException as e:
            # Avoid leaking the API key via URLs inside exception strings.
            raise GeminiError(f"Gemini request failed (network error): {type(e).__name__}") from e

        # Rate limit handling: sleep briefly and retry a couple times.
        if resp.status_code == 429 and attempt <= cfg.max_retries:
            retry_s = _compute_retry_sleep_s(resp)
            if retry_s is None:
                # Exponential-ish fallback: 1s, 2s, 4s...
                retry_s = float(2 ** (attempt - 1))
            retry_s = min(max(retry_s, 0.0), cfg.max_retry_sleep_s)
            time.sleep(retry_s)
            continue

        if resp.status_code >= 400:
            raise GeminiError(f"Gemini HTTP {resp.status_code}: {resp.text[:500]}")

        try:
            data = resp.json()
        except ValueError as e:
            raise GeminiError(f"Gemini returned non-JSON response: {resp.text[:500]}") from e

        # Expected shape: candidates[0].content.parts[*].text
        try:
            candidates = data.get("candidates") or []
            content = candidates[0].get("content") or {}
            parts = content.get("parts") or []
            texts = [p.get("text") for p in parts if isinstance(p, dict) and isinstance(p.get("text"), str)]
        except Exception as e:
            raise GeminiError(f"Unexpected Gemini response shape: {str(data)[:500]}") from e

        text = "".join(texts).strip()
        if not text:
            raise GeminiError("Gemini returned empty text")

        return text
