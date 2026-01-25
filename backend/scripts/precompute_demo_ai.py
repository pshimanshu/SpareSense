#!/usr/bin/env python3
"""
Precompute Gemini outputs for the seeded demo user and save them to disk.

This makes hackathon demos resilient to HTTP 429 rate limits.

Usage (from repo root):
  python3 backend/scripts/precompute_demo_ai.py

Notes:
- Requires GEMINI_API_KEY to be configured (e.g., via .env).
- Writes to backend/app/ai/precomputed/{user_id}_savings_tips.json and {user_id}_flashcards.json
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> int:
    repo = _repo_root()
    load_dotenv(dotenv_path=repo / ".env")

    import sys

    sys.path.insert(0, str(repo))

    from backend.app.ai.llm_service import generate_flashcards, generate_savings_tips
    from backend.app.ai.schemas import AiSpendingSummaryRequest

    req_path = repo / "backend/app/ai/SampleSchemas/AiSpendingSummaryRequest.json"
    payload_dict = json.loads(req_path.read_text(encoding="utf-8"))
    payload = AiSpendingSummaryRequest.model_validate(payload_dict)

    out_dir = repo / "backend/app/ai/precomputed"
    out_dir.mkdir(parents=True, exist_ok=True)

    user_id = payload.user_context.user_id

    tips = generate_savings_tips(payload)
    cards = generate_flashcards(payload)

    # Persist exactly what we will serve (includes meta fields).
    (out_dir / f"{user_id}_savings_tips.json").write_text(tips.model_dump_json(indent=2), encoding="utf-8")
    (out_dir / f"{user_id}_flashcards.json").write_text(cards.model_dump_json(indent=2), encoding="utf-8")

    print("OK")
    print("Wrote:")
    print(f"- backend/app/ai/precomputed/{user_id}_savings_tips.json")
    print(f"- backend/app/ai/precomputed/{user_id}_flashcards.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

