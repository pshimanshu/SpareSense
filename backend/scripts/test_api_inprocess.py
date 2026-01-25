#!/usr/bin/env python3
"""
In-process smoke test for the FastAPI AI endpoints (no network bind required).

Useful when the environment blocks binding to localhost ports.

Run from repo root:
  python3 backend/scripts/test_api_inprocess.py
"""

from __future__ import annotations

import warnings

# Silence noisy SSL backend warning from urllib3 on macOS system Python.
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL*", category=Warning)

import json
import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    # backend/scripts/test_api_inprocess.py -> repo root is 2 levels up
    return Path(__file__).resolve().parents[2]


def main() -> int:
    sys.path.insert(0, str(_repo_root()))

    from fastapi.testclient import TestClient

    from backend.app.ai.schemas import AiFlashcardsResponse, AiSavingsTipsResponse
    from backend.app.main import app

    # Default behavior: tests pass in both modes (Gemini or fallback).
    # If you set GEMINI_REQUIRED=1, the test will fail unless Gemini is used.
    require_gemini = bool(os.getenv("GEMINI_REQUIRED", "").strip())
    expect_gemini = bool(os.getenv("GEMINI_API_KEY", "").strip())

    req_path = _repo_root() / "backend/app/ai/SampleSchemas/AiSpendingSummaryRequest.json"
    payload = json.loads(req_path.read_text(encoding="utf-8"))

    client = TestClient(app)

    tips_r = client.post("/ai/savings-tips", json=payload)
    assert tips_r.status_code == 200, tips_r.text
    tips = AiSavingsTipsResponse.model_validate(tips_r.json())

    cards_r = client.post("/ai/flashcards", json=payload)
    assert cards_r.status_code == 200, cards_r.text
    cards = AiFlashcardsResponse.model_validate(cards_r.json())

    if require_gemini:
        assert expect_gemini, "GEMINI_REQUIRED is set but GEMINI_API_KEY is missing/empty"
        assert tips.meta.fallback_used is False and tips.meta.generated_by == "gemini", (
            "GEMINI_REQUIRED is set, but /ai/savings-tips used fallback. "
            f"Got fallback_used={tips.meta.fallback_used} generated_by={tips.meta.generated_by!r}"
        )
        assert cards.meta.fallback_used is False and cards.meta.generated_by == "gemini", (
            "GEMINI_REQUIRED is set, but /ai/flashcards used fallback. "
            f"Got fallback_used={cards.meta.fallback_used} generated_by={cards.meta.generated_by!r}"
        )
    else:
        # Non-strict mode: accept either Gemini or fallback, but ensure meta flags are consistent.
        assert (tips.meta.generated_by == "gemini") == (tips.meta.fallback_used is False), "tips meta inconsistent"
        assert (cards.meta.generated_by == "gemini") == (cards.meta.fallback_used is False), "flashcards meta inconsistent"

    print("OK")
    print(f"- expect_gemini={expect_gemini}")
    print(f"- require_gemini={require_gemini}")
    print(f"- /ai/savings-tips: tips={len(tips.tips)} fallback_used={tips.meta.fallback_used} generated_by={tips.meta.generated_by}")
    print(
        f"- /ai/flashcards: flashcards={len(cards.flashcards)} fallback_used={cards.meta.fallback_used} generated_by={cards.meta.generated_by}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
