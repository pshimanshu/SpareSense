from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from .schemas import AiFlashcardsResponse, AiSavingsTipsResponse, AiSpendingSummaryRequest


def _precomputed_dir() -> Path:
    # Default to a repo-committable folder containing demo outputs.
    val = os.getenv("AI_PRECOMPUTED_DIR", "").strip()
    if val:
        return Path(val)
    return Path(__file__).parent / "precomputed"


def _demo_user_id() -> str:
    return os.getenv("AI_DEMO_USER_ID", "alex_demo").strip() or "alex_demo"


def _enabled() -> bool:
    # Enabled by default so the demo is bulletproof.
    val = os.getenv("AI_USE_PRECOMPUTED", "1").strip().lower()
    return val not in {"0", "false", "no", "off"}


def _path_for(user_id: str, kind: str) -> Path:
    # kind: "savings_tips" | "flashcards"
    return _precomputed_dir() / f"{user_id}_{kind}.json"


def load_precomputed_savings_tips(payload: AiSpendingSummaryRequest) -> Optional[AiSavingsTipsResponse]:
    """
    If precomputed outputs exist for the demo user, return them.

    This avoids Gemini rate limits during hackathon demos.
    """
    if not _enabled():
        return None
    if payload.user_context.user_id != _demo_user_id():
        return None

    path = _path_for(payload.user_context.user_id, "savings_tips")
    if not path.exists():
        return None

    try:
        return AiSavingsTipsResponse.model_validate_json(path.read_text(encoding="utf-8"))
    except ValidationError:
        # If the file is malformed, ignore and let router continue to Gemini/fallback.
        return None


def load_precomputed_flashcards(payload: AiSpendingSummaryRequest) -> Optional[AiFlashcardsResponse]:
    if not _enabled():
        return None
    if payload.user_context.user_id != _demo_user_id():
        return None

    path = _path_for(payload.user_context.user_id, "flashcards")
    if not path.exists():
        return None

    try:
        return AiFlashcardsResponse.model_validate_json(path.read_text(encoding="utf-8"))
    except ValidationError:
        return None

