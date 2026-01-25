from __future__ import annotations

from fastapi import APIRouter

from .fallbacks import flashcards_fallback, savings_tips_fallback
from .schemas import AiFlashcardsResponse, AiSpendingSummaryRequest, AiSavingsTipsResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/savings-tips", response_model=AiSavingsTipsResponse)
def savings_tips(payload: AiSpendingSummaryRequest) -> AiSavingsTipsResponse:
    # Gemini integration comes next; fallback ensures a stable demo and contract-valid JSON.
    return savings_tips_fallback(payload)


@router.post("/flashcards", response_model=AiFlashcardsResponse)
def flashcards(payload: AiSpendingSummaryRequest) -> AiFlashcardsResponse:
    return flashcards_fallback(payload)

