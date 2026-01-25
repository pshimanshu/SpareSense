#!/usr/bin/env bash
set -euo pipefail

# Quick sanity checks for hackathon demos.
# - Does not require Gemini to be available (precomputed mode makes demo stable).
#
# Usage:
#   bash backend/scripts/hackathon_check.sh

PY="${PYTHON:-}"
if [[ -z "$PY" ]]; then
  if [[ -x "backend/.venv/bin/python" ]]; then
    PY="backend/.venv/bin/python"
  elif [[ -x "backend/venv/bin/python" ]]; then
    PY="backend/venv/bin/python"
  else
    PY="python3"
  fi
fi

export PYTHONDONTWRITEBYTECODE=1

echo "==> Offline fallback + contract validation"
"$PY" backend/scripts/validate_fallbacks.py
echo

echo "==> In-process API smoke test"
"$PY" backend/scripts/test_api_inprocess.py
echo

echo "==> Unit tests"
"$PY" -m unittest discover -s backend/tests
echo

echo "OK: hackathon checks passed"
