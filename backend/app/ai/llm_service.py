from __future__ import annotations

import json
import re
from pathlib import Path

from pydantic import ValidationError

from .gemini_client import GeminiError, generate_text, load_gemini_config_from_env
from .schemas import AiFlashcardsResponse, AiSavingsTipsResponse, AiSpendingSummaryRequest


class LlmParseError(RuntimeError):
    pass


PROMPTS_DIR = Path(__file__).parent / "prompts"


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


def generate_savings_tips(payload: AiSpendingSummaryRequest) -> AiSavingsTipsResponse:
    cfg = load_gemini_config_from_env()

    template = _load_prompt("savings_tips.txt")
    # Keep the model input compact to avoid prompt bloat and token-limit truncation.
    input_json = payload.model_dump_json(exclude_none=True)
    prompt = _render_prompt(
        template,
        input_json=input_json,
        tip_count=payload.constraints.tip_count,
        flashcard_count=payload.constraints.flashcard_count,
    )

    raw = generate_text(prompt, cfg=cfg)
    json_str = _extract_json(raw)

    try:
        resp = AiSavingsTipsResponse.model_validate_json(json_str)
    except ValidationError as e:
        raise LlmParseError(f"Gemini output failed schema validation: {e}") from e

    # Ensure meta is consistent even if the model deviates.
    resp.meta.generated_by = "gemini"
    resp.meta.fallback_used = False
    return resp


def generate_flashcards(payload: AiSpendingSummaryRequest) -> AiFlashcardsResponse:
    cfg = load_gemini_config_from_env()

    template = _load_prompt("flashcards.txt")
    input_json = payload.model_dump_json(exclude_none=True)
    prompt = _render_prompt(
        template,
        input_json=input_json,
        tip_count=payload.constraints.tip_count,
        flashcard_count=payload.constraints.flashcard_count,
    )

    raw = generate_text(prompt, cfg=cfg)
    json_str = _extract_json(raw)

    try:
        resp = AiFlashcardsResponse.model_validate_json(json_str)
    except ValidationError as e:
        raise LlmParseError(f"Gemini output failed schema validation: {e}") from e

    resp.meta.generated_by = "gemini"
    resp.meta.fallback_used = False
    return resp


def _pretty_json_for_debug(obj: object) -> str:
    return json.dumps(obj, indent=2, sort_keys=True)
