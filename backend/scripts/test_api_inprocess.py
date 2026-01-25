#!/usr/bin/env python3
"""
In-process smoke test for the FastAPI AI endpoints (no network bind required).

Useful when the environment blocks binding to localhost ports.

Run from repo root:
  python3 backend/scripts/test_api_inprocess.py
"""

from __future__ import annotations

import json
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

    req_path = _repo_root() / "backend/app/ai/SampleSchemas/AiSpendingSummaryRequest.json"
    payload = json.loads(req_path.read_text(encoding="utf-8"))

    client = TestClient(app)

    tips_r = client.post("/ai/savings-tips", json=payload)
    assert tips_r.status_code == 200, tips_r.text
    tips = AiSavingsTipsResponse.model_validate(tips_r.json())

    cards_r = client.post("/ai/flashcards", json=payload)
    assert cards_r.status_code == 200, cards_r.text
    cards = AiFlashcardsResponse.model_validate(cards_r.json())

    print("OK")
    print(f"- /ai/savings-tips: tips={len(tips.tips)} fallback_used={tips.meta.fallback_used} generated_by={tips.meta.generated_by}")
    print(
        f"- /ai/flashcards: flashcards={len(cards.flashcards)} fallback_used={cards.meta.fallback_used} generated_by={cards.meta.generated_by}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

