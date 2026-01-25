from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from fastapi import Header

from .fallbacks import flashcards_fallback, savings_tips_fallback
from .gemini_client import GeminiError
from .llm_service import LlmParseError, generate_flashcards, generate_savings_tips
from .precomputed_store import load_precomputed_flashcards, load_precomputed_savings_tips
from .schemas import AiFlashcardsResponse, AiSpendingSummaryRequest, AiSavingsTipsResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/savings-tips", response_model=AiSavingsTipsResponse)
def savings_tips(
    payload: AiSpendingSummaryRequest,
    x_ai_bypass_precomputed: Optional[str] = Header(default=None, alias="X-AI-Bypass-Precomputed"),
) -> AiSavingsTipsResponse:
    bypass = bool(x_ai_bypass_precomputed and x_ai_bypass_precomputed.strip() not in {"0", "false", "no", "off"})
    pre = None if bypass else load_precomputed_savings_tips(payload)
    if pre is not None:
        return pre
    try:
        return generate_savings_tips(payload)
    except (GeminiError, LlmParseError):
        return savings_tips_fallback(payload)


@router.post("/flashcards", response_model=AiFlashcardsResponse)
def flashcards(
    payload: AiSpendingSummaryRequest,
    x_ai_bypass_precomputed: Optional[str] = Header(default=None, alias="X-AI-Bypass-Precomputed"),
) -> AiFlashcardsResponse:
    bypass = bool(x_ai_bypass_precomputed and x_ai_bypass_precomputed.strip() not in {"0", "false", "no", "off"})
    pre = None if bypass else load_precomputed_flashcards(payload)
    if pre is not None:
        return pre
    try:
        return generate_flashcards(payload)
    except (GeminiError, LlmParseError):
        return flashcards_fallback(payload)
