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
├─ docs/ # Architecture & demo notes (to be added)
├─ scripts/ # Utility scripts
└─ README.md

