# 💸 FinWise — Smart Spending & Micro-Savings Assistant

FinWise is a hackathon project that helps users **understand their spending, learn better financial habits, and save money automatically** — all in a fun, low-friction way.

Built for the **Capital One: Best Financial Hack** challenge.

---

## 🚀 Project Overview

FinWise combines transaction analysis, AI insights, gamification, and micro-savings to help users make smarter financial decisions.

### Core Features

- 📊 **Spending Analysis**
  - Pulls mock transaction data using the Capital One **Nessie API**
  - Groups transactions by category and merchant
  - Identifies recurring and high-impact spending patterns

- 🤖 **AI-Powered Financial Insights**
  - Uses **Google Gemini API** to generate personalized savings suggestions
  - Translates raw transaction data into actionable advice

- 🎮 **Gamified Financial Learning**
  - Interactive flashcard questions based on the user’s spending habits
  - Encourages financial literacy through short, engaging challenges

- 💰 **Micro-Savings Bot**
  - Automatically rounds up purchases to the nearest dollar
  - Saves spare change into a dedicated savings balance
  - Simulated or real investment flow using **Solana (Devnet)**

---

## 🏗️ Tech Stack

**Frontend**
- React + Vite
- Tailwind CSS
- Charting libraries for spending visualization

**Backend**
- FastAPI (Python)
- Capital One Nessie API
- Google Gemini API

**Blockchain**
- Solana (Devnet or simulated mode)

---

## 📁 Project Structure
finwise/
├─ backend/ # FastAPI backend (API, AI, savings logic)
├─ frontend/ # React frontend (UI & dashboard)
└─ README.md

---

## 🤝 AI Data Contracts (DEV 2)

The AI endpoints use a **versioned JSON contract** so the frontend and backend stay in sync and Gemini prompts can be forced to return stable output.

Source of truth (Pydantic models):
- `backend/app/ai/schemas.py`

Sample JSON payloads (ready to use for mock API calls / frontend dev):
- `backend/app/ai/SampleSchemas/AiSpendingSummaryRequest.json`
- `backend/app/ai/SampleSchemas/AiSavingsTipsResponse.json`
- `backend/app/ai/SampleSchemas/AiFlashcardsResponse.json`

Prompt templates (used to force Gemini to return contract-valid JSON):
- `backend/app/ai/prompts/savings_tips.txt`
- `backend/app/ai/prompts/flashcards.txt`

Deterministic fallbacks (demo-safe responses that always match the contract):
- `backend/app/ai/fallbacks.py`

### Shared Request Body (input JSON)

Both AI endpoints accept the same request body:
- `AiSpendingSummaryRequest`
  - `spending_summary.category_totals`: category totals and counts
  - `spending_summary.top_merchants`: top merchant totals and counts
  - Optional enrichments: `silent_spenders`, `recurring_merchants`
  - `income.monthly_income` + `income.confidence` (0..1)
  - `constraints.tip_count` (1..10) and `constraints.flashcard_count` (1..20) to control response size

### Savings Tips Response (output JSON)

- `AiSavingsTipsResponse`
  - `tips[]`: each tip includes `estimated_monthly_savings`, `confidence` (0..1), and an optional `evidence` block + `nudge`
  - `totals.estimated_monthly_savings_total`: sum of the tip estimates

### Flashcards Response (output JSON)

- `AiFlashcardsResponse`
  - `flashcards[]`: `type`, `skill`, `question`, `options`, `answer`, `explanation`, and optional `data` for UI context

### Planned AI Endpoints

These are the endpoints the backend will expose for DEV 2:
- `POST /ai/savings-tips` -> `AiSavingsTipsResponse`
- `POST /ai/flashcards` -> `AiFlashcardsResponse`

### Demo-Safe Behavior (Fallbacks)

Until Gemini is fully wired, the backend can return deterministic responses that:
- Always return exactly `constraints.tip_count` tips and `constraints.flashcard_count` flashcards
- Set `meta.fallback_used = true` and `meta.generated_by = "fallback"`
