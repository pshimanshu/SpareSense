"""
Data contracts (request/response JSON shapes) for the AI endpoints.

Why this exists:
- Gives the backend + frontend a stable, versioned JSON contract.
- Provides validation at the API boundary (Pydantic) before hitting any LLM.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


# Bump this when you introduce breaking changes to request/response shapes.
SchemaVersion = Literal["1.0"]


# -----------------------------
# Shared request (input JSON)
# -----------------------------


class UserContext(BaseModel):
    user_id: str = Field(..., examples=["alex_demo"])
    currency: str = Field(default="USD", examples=["USD"])
    timezone: Optional[str] = Field(default=None, examples=["America/Florida"])


class Period(BaseModel):
    start_date: date
    end_date: date


class Income(BaseModel):
    monthly_income: Optional[float] = Field(default=None, ge=0)
    confidence: float = Field(default=0.5, ge=0, le=1)


class CategoryTotal(BaseModel):
    category: str
    amount: float = Field(..., ge=0)
    transaction_count: int = Field(..., ge=0)


class MerchantTotal(BaseModel):
    merchant: str
    amount: float = Field(..., ge=0)
    transaction_count: int = Field(..., ge=0)
    category_hint: Optional[str] = None


class SilentSpender(BaseModel):
    """
    "Silent spenders" are small, frequent purchases that add up.
    """

    label: str
    category: Optional[str] = None
    avg_amount: Optional[float] = Field(default=None, ge=0)
    transaction_count: int = Field(..., ge=0)
    amount: float = Field(..., ge=0)


class RecurringMerchant(BaseModel):
    merchant: str
    category_hint: Optional[str] = None
    amount_per_period: float = Field(..., ge=0)
    cadence: Literal["weekly", "biweekly", "monthly", "quarterly", "yearly", "unknown"] = "unknown"
    last_charge_date: Optional[date] = None
    confidence: float = Field(default=0.5, ge=0, le=1)


class SpendingSummary(BaseModel):
    total_spend: float = Field(..., ge=0)
    transaction_count: int = Field(..., ge=0)

    # Arrays (not maps) keep ordering explicit and avoid dynamic keys.
    category_totals: list[CategoryTotal] = Field(default_factory=list)
    top_merchants: list[MerchantTotal] = Field(default_factory=list)

    # Optional enrichments your analyzer can populate over time.
    silent_spenders: list[SilentSpender] = Field(default_factory=list)
    recurring_merchants: list[RecurringMerchant] = Field(default_factory=list)


class Constraints(BaseModel):
    # Controls output count deterministically (important for LLM + frontend stability).
    tip_count: int = Field(default=3, ge=1, le=10)
    flashcard_count: int = Field(default=5, ge=1, le=20)


class AiSpendingSummaryRequest(BaseModel):
    schema_version: SchemaVersion = "1.0"
    user_context: UserContext
    period: Period
    income: Income = Field(default_factory=Income)
    spending_summary: SpendingSummary
    constraints: Constraints = Field(default_factory=Constraints)


# -----------------------------
# Savings tips response
# -----------------------------


class TipEvidence(BaseModel):
    based_on: list[Literal["top_merchants", "category_totals", "silent_spenders", "recurring_merchants"]] = Field(
        default_factory=list
    )
    merchant: Optional[str] = None
    current_monthly_spend: Optional[float] = Field(default=None, ge=0)
    assumption: Optional[str] = None


class SavingsTip(BaseModel):
    id: str
    title: str
    recommendation: str
    estimated_monthly_savings: float = Field(..., ge=0)
    confidence: float = Field(..., ge=0, le=1)
    category_targets: list[str] = Field(default_factory=list)
    evidence: Optional[TipEvidence] = None
    nudge: Optional[str] = None


class SavingsTotals(BaseModel):
    estimated_monthly_savings_total: float = Field(..., ge=0)


class ResponseMeta(BaseModel):
    generated_by: Literal["gemini", "fallback", "unknown"] = "unknown"
    fallback_used: bool = False


class AiSavingsTipsResponse(BaseModel):
    schema_version: SchemaVersion = "1.0"
    period: Period
    currency: str = "USD"
    tips: list[SavingsTip] = Field(default_factory=list)
    totals: SavingsTotals
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


# -----------------------------
# Flashcards response
# -----------------------------


FlashcardType = Literal["multiple_choice", "true_false", "guess_the_number", "reflection"]
FlashcardSkill = Literal["awareness", "prediction", "habit_reinforcement", "math", "commitment"]
FlashcardDifficulty = Literal["easy", "medium", "hard"]


class Flashcard(BaseModel):
    id: str
    type: FlashcardType
    skill: FlashcardSkill
    question: str
    options: list[str] = Field(default_factory=list)
    answer: str
    explanation: str
    difficulty: FlashcardDifficulty = "easy"
    data: dict[str, Any] = Field(default_factory=dict)


class AiFlashcardsResponse(BaseModel):
    schema_version: SchemaVersion = "1.0"
    period: Period
    currency: str = "USD"
    flashcards: list[Flashcard] = Field(default_factory=list)
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
