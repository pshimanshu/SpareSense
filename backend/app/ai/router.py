from __future__ import annotations

from fastapi import APIRouter

from .fallbacks import flashcards_fallback, savings_tips_fallback
from .llm_service import GeminiError, LlmParseError, generate_flashcards, generate_savings_tips
from .precomputed_store import load_precomputed_flashcards, load_precomputed_savings_tips
from .schemas import AiFlashcardsResponse, AiSpendingSummaryRequest, AiSavingsTipsResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/savings-tips", response_model=AiSavingsTipsResponse)
def savings_tips(payload: AiSpendingSummaryRequest) -> AiSavingsTipsResponse:
    pre = load_precomputed_savings_tips(payload)
    if pre is not None:
        return pre
    try:
        return generate_savings_tips(payload)
    except (GeminiError, LlmParseError):
        return savings_tips_fallback(payload)


@router.post("/flashcards", response_model=AiFlashcardsResponse)
def flashcards(payload: AiSpendingSummaryRequest) -> AiFlashcardsResponse:
    pre = load_precomputed_flashcards(payload)
    if pre is not None:
        return pre
    try:
        return generate_flashcards(payload)
    except (GeminiError, LlmParseError):
        return flashcards_fallback(payload)
