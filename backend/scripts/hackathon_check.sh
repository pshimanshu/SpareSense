#!/usr/bin/env bash
set -euo pipefail

# Quick sanity checks for hackathon demos.
# - Does not require Gemini to be available (precomputed mode makes demo stable).
#
# Usage:
#   bash backend/scripts/hackathon_check.sh

echo "==> Offline fallback + contract validation"
backend/.venv/bin/python backend/scripts/validate_fallbacks.py
echo

echo "==> In-process API smoke test"
backend/.venv/bin/python backend/scripts/test_api_inprocess.py
echo

echo "==> Unit tests"
backend/.venv/bin/python -m unittest discover -s backend/tests
echo

echo "OK: hackathon checks passed"

