#!/usr/bin/env python3
"""
Offline validation for the AI data contracts + deterministic fallbacks.

This does NOT call FastAPI or Gemini. It:
1) Validates the sample request JSON against AiSpendingSummaryRequest
2) Runs the fallback generators
3) Validates responses and checks counts/meta fields

Run from repo root:
  python3 backend/scripts/validate_fallbacks.py
  REQ_FILE=backend/app/ai/SampleSchemas/AiSpendingSummaryRequest.json python3 backend/scripts/validate_fallbacks.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    # backend/scripts/validate_fallbacks.py -> repo root is 2 levels up
    return Path(__file__).resolve().parents[2]


def main() -> int:
    sys.path.insert(0, str(_repo_root()))

    from backend.app.ai.fallbacks import flashcards_fallback, savings_tips_fallback
    from backend.app.ai.schemas import AiSpendingSummaryRequest

    req_file = os.getenv("REQ_FILE", "backend/app/ai/SampleSchemas/AiSpendingSummaryRequest.json")
    req_path = _repo_root() / req_file

    payload_dict = json.loads(req_path.read_text(encoding="utf-8"))
    payload = AiSpendingSummaryRequest.model_validate(payload_dict)

    tips_resp = savings_tips_fallback(payload)
    cards_resp = flashcards_fallback(payload)

    assert len(tips_resp.tips) == payload.constraints.tip_count, "tip_count mismatch"
    assert tips_resp.meta.fallback_used is True and tips_resp.meta.generated_by == "fallback", "tips meta mismatch"

    assert len(cards_resp.flashcards) == payload.constraints.flashcard_count, "flashcard_count mismatch"
    assert cards_resp.meta.fallback_used is True and cards_resp.meta.generated_by == "fallback", "flashcards meta mismatch"

    print("OK")
    print(f"- tips: {len(tips_resp.tips)} (fallback_used={tips_resp.meta.fallback_used})")
    print(f"- flashcards: {len(cards_resp.flashcards)} (fallback_used={cards_resp.meta.fallback_used})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

