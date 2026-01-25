import warnings
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL*", category=Warning)

import json
import os
import unittest
from pathlib import Path


class TestAiContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Ensure repo root is on path when running via `python -m unittest`.
        import sys

        cls.repo_root = Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(cls.repo_root))

    def _load_sample_request(self) -> dict:
        req_path = self.repo_root / "backend/app/ai/SampleSchemas/AiSpendingSummaryRequest.json"
        return json.loads(req_path.read_text(encoding="utf-8"))

    def test_sample_request_validates(self) -> None:
        from backend.app.ai.schemas import AiSpendingSummaryRequest

        payload = self._load_sample_request()
        AiSpendingSummaryRequest.model_validate(payload)

    def test_endpoints_return_contract_valid_json(self) -> None:
        # Ensure the test is deterministic: if GEMINI_REQUIRED is set, this test
        # may fail under rate limits. Prefer running gemini-required checks separately.
        os.environ.pop("GEMINI_REQUIRED", None)

        from fastapi.testclient import TestClient

        from backend.app.ai.schemas import AiFlashcardsResponse, AiSavingsTipsResponse
        from backend.app.main import app

        client = TestClient(app)
        payload = self._load_sample_request()

        r1 = client.post("/ai/savings-tips", json=payload)
        self.assertEqual(r1.status_code, 200, r1.text)
        tips = AiSavingsTipsResponse.model_validate(r1.json())
        self.assertEqual(len(tips.tips), payload["constraints"]["tip_count"])

        r2 = client.post("/ai/flashcards", json=payload)
        self.assertEqual(r2.status_code, 200, r2.text)
        cards = AiFlashcardsResponse.model_validate(r2.json())
        self.assertEqual(len(cards.flashcards), payload["constraints"]["flashcard_count"])


if __name__ == "__main__":
    unittest.main()
