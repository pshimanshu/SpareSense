from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from pydantic import ValidationError

from .gemini_client import GeminiError, generate_text, load_gemini_config_from_env
from .schemas import AiFlashcardsResponse, AiSavingsTipsResponse, AiSpendingSummaryRequest


class LlmParseError(RuntimeError):
    pass


PROMPTS_DIR = Path(__file__).parent / "prompts"

# In-memory cache to reduce rate-limit pressure during demos.
# Keyed by a hash of prompt + payload + model config.
_CACHE: Dict[str, Tuple[float, Any]] = {}


def _cache_get(key: str) -> Optional[Any]:
    item = _CACHE.get(key)
    if not item:
        return None
    expires_at, value = item
    if time.time() >= expires_at:
        _CACHE.pop(key, None)
        return None
    # Return a defensive copy if it's a Pydantic model.
    if hasattr(value, "model_copy"):
        return value.model_copy(deep=True)
    return value


def _cache_set(key: str, value: Any, *, ttl_s: float) -> None:
    if ttl_s <= 0:
        return
    _CACHE[key] = (time.time() + ttl_s, value)


def _cache_ttl_s_from_env() -> float:
    """
    How long to cache successful Gemini responses in-memory.
    Helps avoid hitting free-tier rate limits during iterative dev/demo.
    """
    val = (os.getenv("GEMINI_CACHE_TTL_S", "600") or "600").strip()
    try:
        return float(val)
    except ValueError:
        return 600.0


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    return path.read_text(encoding="utf-8")


def _render_prompt(template: str, *, input_json: str, tip_count: int, flashcard_count: int) -> str:
    # Simple token replacement keeps templates readable and avoids pulling in a templating lib.
    return (
        template.replace("{{input_json}}", input_json)
        .replace("{{tip_count}}", str(tip_count))
        .replace("{{flashcard_count}}", str(flashcard_count))
    )


_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)


def _extract_json(text: str) -> str:
    """
    Gemini *should* return pure JSON, but this makes us resilient if it returns
    code fences or surrounding commentary.
    """
    t = text.strip()

    m = _FENCE_RE.search(t)
    if m:
        t = m.group(1).strip()

    # If we still have extra text, try to slice the first JSON object/array.
    first_obj = t.find("{")
    first_arr = t.find("[")
    if first_obj == -1 and first_arr == -1:
        raise LlmParseError("No JSON object/array found in model output")

    start = min([i for i in (first_obj, first_arr) if i != -1])
    end_obj = t.rfind("}")
    end_arr = t.rfind("]")
    end = max(end_obj, end_arr)
    if end == -1 or end <= start:
        raise LlmParseError("Could not determine JSON boundaries in model output")

    return t[start : end + 1].strip()


def _generate_and_validate_json(
    *,
    payload: AiSpendingSummaryRequest,
    prompt_name: str,
    validator,
    repair_label: str,
):
    """
    Produce contract-valid JSON from Gemini with one repair retry.
    """
    cfg = load_gemini_config_from_env()

    template = _load_prompt(prompt_name)
    # Keep the model input compact to avoid prompt bloat and token-limit truncation.
    input_json = payload.model_dump_json(exclude_none=True)
    prompt = _render_prompt(
        template,
        input_json=input_json,
        tip_count=payload.constraints.tip_count,
        flashcard_count=payload.constraints.flashcard_count,
    )

    # Cache key: include model + prompt name + rendered prompt (which includes counts and input JSON).
    cache_ttl_s = _cache_ttl_s_from_env()

    h = hashlib.sha256()
    h.update(cfg.model.encode("utf-8"))
    h.update(b"\n")
    h.update(prompt_name.encode("utf-8"))
    h.update(b"\n")
    h.update(prompt.encode("utf-8"))
    cache_key = h.hexdigest()

    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    raw_1 = generate_text(prompt, cfg=cfg)
    try:
        json_1 = _extract_json(raw_1)
        validated = validator(json_1)
        _cache_set(cache_key, validated, ttl_s=cache_ttl_s)
        return validated
    except (LlmParseError, ValidationError):
        # One retry: ask Gemini to re-emit a complete JSON object matching the contract.
        repair_prompt = (
            "Return ONLY valid JSON (no markdown/backticks). Output MUST be a complete JSON object.\n"
            "Your previous output was invalid, incomplete, or did not match the contract.\n\n"
            f"Task: output a valid {repair_label} JSON object.\n"
            f"Counts: tip_count={payload.constraints.tip_count}, flashcard_count={payload.constraints.flashcard_count}\n\n"
            "Input JSON (source of truth):\n"
            f"{input_json}\n\n"
            "Previous output to fix (may be incomplete):\n"
            f"{raw_1}\n"
        )
        raw_2 = generate_text(repair_prompt, cfg=cfg)
        json_2 = _extract_json(raw_2)
        validated = validator(json_2)
        _cache_set(cache_key, validated, ttl_s=cache_ttl_s)
        return validated


def generate_savings_tips(payload: AiSpendingSummaryRequest) -> AiSavingsTipsResponse:
    try:
        resp = _generate_and_validate_json(
            payload=payload,
            prompt_name="savings_tips.txt",
            validator=AiSavingsTipsResponse.model_validate_json,
            repair_label="AiSavingsTipsResponse",
        )
    except (ValidationError, LlmParseError) as e:
        raise LlmParseError(f"Gemini output failed schema validation: {e}") from e

    # Ensure meta is consistent even if the model deviates.
    resp.meta.generated_by = "gemini"
    resp.meta.fallback_used = False
    return resp


def generate_flashcards(payload: AiSpendingSummaryRequest) -> AiFlashcardsResponse:
    try:
        resp = _generate_and_validate_json(
            payload=payload,
            prompt_name="flashcards.txt",
            validator=AiFlashcardsResponse.model_validate_json,
            repair_label="AiFlashcardsResponse",
        )
    except (ValidationError, LlmParseError) as e:
        raise LlmParseError(f"Gemini output failed schema validation: {e}") from e

    resp.meta.generated_by = "gemini"
    resp.meta.fallback_used = False
    return resp


def _pretty_json_for_debug(obj: object) -> str:
    return json.dumps(obj, indent=2, sort_keys=True)
