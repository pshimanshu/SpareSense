#!/usr/bin/env bash
set -euo pipefail

# Smoke-test the AI endpoints using the sample request payload.
# Usage:
#   backend/scripts/smoke_ai.sh
#   API_BASE_URL=http://localhost:8000 backend/scripts/smoke_ai.sh

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
REQ_FILE="backend/app/ai/SampleSchemas/AiSpendingSummaryRequest.json"

echo "Using API_BASE_URL=$API_BASE_URL"
echo "Using request file: $REQ_FILE"
echo

echo "==> POST /ai/savings-tips"
curl -sS \
  -X POST "$API_BASE_URL/ai/savings-tips" \
  -H "Content-Type: application/json" \
  --data-binary @"$REQ_FILE"
echo
echo

echo "==> POST /ai/flashcards"
curl -sS \
  -X POST "$API_BASE_URL/ai/flashcards" \
  -H "Content-Type: application/json" \
  --data-binary @"$REQ_FILE"
echo
