from __future__ import annotations

"""
Deterministic fallback responses for the AI endpoints.

Why this exists:
- Hackathon demos should never fail due to an LLM outage / bad JSON / API quota.
- Keeps frontend integration stable while Gemini integration is being built.
"""

from typing import Any, Optional, Tuple

from .schemas import (
    AiFlashcardsResponse,
    AiSavingsTipsResponse,
    AiSpendingSummaryRequest,
    Flashcard,
    ResponseMeta,
    SavingsTip,
    SavingsTotals,
    TipEvidence,
)


def _top_category(req: AiSpendingSummaryRequest) -> Tuple[Optional[str], Optional[float]]:
    if not req.spending_summary.category_totals:
        return None, None
    top = max(req.spending_summary.category_totals, key=lambda c: c.amount)
    return top.category, top.amount


def _top_merchant(req: AiSpendingSummaryRequest) -> Tuple[Optional[str], Optional[float]]:
    if not req.spending_summary.top_merchants:
        return None, None
    top = max(req.spending_summary.top_merchants, key=lambda m: m.amount)
    return top.merchant, top.amount


def savings_tips_fallback(req: AiSpendingSummaryRequest) -> AiSavingsTipsResponse:
    """
    Returns a contract-valid tips response with conservative estimates.
    """
    n = req.constraints.tip_count
    currency = req.user_context.currency

    top_category, top_category_amt = _top_category(req)
    top_merchant, top_merchant_amt = _top_merchant(req)

    tips: list[SavingsTip] = []

    # 1) Target the highest spend merchant if available; else the top category.
    if top_merchant and top_merchant_amt is not None:
        est = round(top_merchant_amt * 0.25, 2)
        tips.append(
            SavingsTip(
                id="tip_1",
                title=f"Trim spending at {top_merchant}",
                recommendation=f"Try reducing {top_merchant} purchases by ~25% this month (fewer visits or cheaper default).",
                estimated_monthly_savings=est,
                confidence=0.6,
                category_targets=[],
                evidence=TipEvidence(
                    based_on=["top_merchants"],
                    merchant=top_merchant,
                    current_monthly_spend=top_merchant_amt,
                    assumption="Estimate assumes a 25% reduction on your top merchant spend.",
                ),
                nudge="Choose one default swap (smaller size, skip add-ons) and stick with it.",
            )
        )
    elif top_category and top_category_amt is not None:
        est = round(top_category_amt * 0.2, 2)
        tips.append(
            SavingsTip(
                id="tip_1",
                title=f"Set a cap for {top_category}",
                recommendation=f"Set a weekly cap for {top_category} and track it for 2 weeks.",
                estimated_monthly_savings=est,
                confidence=0.55,
                category_targets=[top_category],
                evidence=TipEvidence(
                    based_on=["category_totals"],
                    current_monthly_spend=top_category_amt,
                    assumption="Estimate assumes a 20% reduction in your top category.",
                ),
                nudge="Write the cap on your lock screen for the next 7 days.",
            )
        )

    # 2) Recurring merchant: cancel/pause one recurring charge (if any).
    if req.spending_summary.recurring_merchants:
        rm = max(req.spending_summary.recurring_merchants, key=lambda r: r.amount_per_period)
        est = round(rm.amount_per_period, 2)
        tips.append(
            SavingsTip(
                id=f"tip_{len(tips)+1}",
                title="Review recurring subscriptions",
                recommendation="Cancel or pause one recurring charge you don’t use weekly.",
                estimated_monthly_savings=est,
                confidence=0.65,
                category_targets=[rm.category_hint] if rm.category_hint else [],
                evidence=TipEvidence(
                    based_on=["recurring_merchants"],
                    merchant=rm.merchant,
                    current_monthly_spend=rm.amount_per_period,
                    assumption="Estimate assumes removing one recurring charge.",
                ),
                nudge="If you haven't used it in 2 weeks, pause it for 1 month.",
            )
        )

    # 3) Silent spender: reduce frequency (if present).
    if req.spending_summary.silent_spenders:
        ss = max(req.spending_summary.silent_spenders, key=lambda s: s.amount)
        est = round(ss.amount * 0.2, 2)
        tips.append(
            SavingsTip(
                id=f"tip_{len(tips)+1}",
                title="Tackle a silent spender",
                recommendation=f"Reduce '{ss.label}' purchases by a small amount (e.g., 1-2 fewer per week).",
                estimated_monthly_savings=est,
                confidence=0.6,
                category_targets=[ss.category] if ss.category else [],
                evidence=TipEvidence(
                    based_on=["silent_spenders"],
                    current_monthly_spend=ss.amount,
                    assumption="Estimate assumes a 20% reduction in this frequent small spend pattern.",
                ),
                nudge="Create a replacement rule: bring a snack/drink from home before buying on the go.",
            )
        )

    # Pad to N with generic-but-safe tips so the UI never breaks.
    while len(tips) < n:
        i = len(tips) + 1
        tips.append(
            SavingsTip(
                id=f"tip_{i}",
                title="Try a 24-hour rule for non-essentials",
                recommendation="Wait 24 hours before making any non-essential purchase over $20.",
                estimated_monthly_savings=20.0,
                confidence=0.4,
                category_targets=[],
                evidence=TipEvidence(based_on=[], assumption="Conservative default estimate for demo stability."),
                nudge="Add items to a wishlist instead of buying immediately.",
            )
        )

    tips = tips[:n]
    total = round(sum(t.estimated_monthly_savings for t in tips), 2)

    return AiSavingsTipsResponse(
        period=req.period,
        currency=currency,
        tips=tips,
        totals=SavingsTotals(estimated_monthly_savings_total=total),
        meta=ResponseMeta(generated_by="fallback", fallback_used=True),
    )


def flashcards_fallback(req: AiSpendingSummaryRequest) -> AiFlashcardsResponse:
    """
    Returns a contract-valid set of flashcards grounded in available spending data.
    """
    n = req.constraints.flashcard_count
    currency = req.user_context.currency

    top_category, top_category_amt = _top_category(req)
    top_merchant, top_merchant_amt = _top_merchant(req)

    cards: list[Flashcard] = []

    # Card 1: awareness (top category)
    if top_category and top_category_amt is not None:
        options = [top_category]
        for c in req.spending_summary.category_totals:
            if c.category != top_category:
                options.append(c.category)
            if len(options) >= 4:
                break
        while len(options) < 4:
            options.append(f"Other {len(options)}")

        cards.append(
            Flashcard(
                id="card_1",
                type="multiple_choice",
                skill="awareness",
                question="Which category did you spend the most on in this period?",
                options=options[:4],
                answer=top_category,
                explanation=f"{top_category} was your highest category by total spend.",
                difficulty="easy",
                data={"category": top_category, "amount": top_category_amt, "currency": currency},
            )
        )

    # Card 2: guess-the-number (top merchant)
    if top_merchant and top_merchant_amt is not None:
        amt = float(top_merchant_amt)
        # 4 rough options around the actual amount; round to nearest 10 for readability.
        base = round(amt, -1)
        opts = sorted({max(0.0, base * f) for f in (0.5, 0.8, 1.0, 1.3)})
        options = [f"{currency} {round(o, -1):,.0f}" for o in opts][:4]
        cards.append(
            Flashcard(
                id=f"card_{len(cards)+1}",
                type="guess_the_number",
                skill="prediction",
                question=f"Guess how much you spent at {top_merchant} (closest wins).",
                options=options,
                answer=f"{currency} {base:,.0f}",
                explanation=f"You spent about {currency} {amt:,.2f} at {top_merchant} in this period.",
                difficulty="medium",
                data={"merchant": top_merchant, "amount": amt, "currency": currency},
            )
        )

    # Card 3: true/false about recurring
    if req.spending_summary.recurring_merchants:
        rm = max(req.spending_summary.recurring_merchants, key=lambda r: r.amount_per_period)
        cards.append(
            Flashcard(
                id=f"card_{len(cards)+1}",
                type="true_false",
                skill="habit_reinforcement",
                question=f"True or False: Your largest recurring charge is {rm.merchant}.",
                options=["True", "False"],
                answer="True",
                explanation=f"{rm.merchant} is the biggest recurring merchant in this period.",
                difficulty="easy",
                data={"merchant": rm.merchant, "amount_per_period": rm.amount_per_period, "currency": currency},
            )
        )

    # Card 4: math (simple savings estimate)
    if top_merchant and top_merchant_amt is not None:
        amt = float(top_merchant_amt)
        est = round(amt * 0.25, 0)
        options = [f"{currency} {v:,.0f}" for v in (0.0, est / 2, est, est * 2)]
        cards.append(
            Flashcard(
                id=f"card_{len(cards)+1}",
                type="multiple_choice",
                skill="math",
                question=f"If you reduce {top_merchant} spending by 25%, about how much could you save?",
                options=options[:4],
                answer=f"{currency} {est:,.0f}",
                explanation="A 25% reduction is a simple starting target for cutting a high-spend merchant.",
                difficulty="medium",
                data={"merchant": top_merchant, "current_spend": amt, "assumed_reduction": 0.25},
            )
        )

    # Card 5: reflection (always included)
    cards.append(
        Flashcard(
            id=f"card_{len(cards)+1}",
            type="reflection",
            skill="commitment",
            question="What’s one small habit you can change this week to save money?",
            options=["Cook 1 extra meal", "Cancel 1 subscription", "Bring coffee from home", "Set a daily spend cap"],
            answer="Any",
            explanation="Pick the easiest change. Consistency matters more than intensity.",
            difficulty="easy",
            data={"note": "reflection_card"},
        )
    )

    # Ensure exactly N cards.
    cards = cards[:n]
    while len(cards) < n:
        i = len(cards) + 1
        cards.append(
            Flashcard(
                id=f"card_{i}",
                type="true_false",
                skill="awareness",
                question="True or False: Tracking spending weekly can improve saving outcomes.",
                options=["True", "False"],
                answer="True",
                explanation="Small, frequent check-ins help you notice patterns before the month ends.",
                difficulty="easy",
                data={"note": "padding_card"},
            )
        )

    return AiFlashcardsResponse(
        period=req.period,
        currency=currency,
        flashcards=cards,
        meta=ResponseMeta(generated_by="fallback", fallback_used=True),
    )


def _demo_only_debug_payload(req: AiSpendingSummaryRequest) -> dict[str, Any]:
    """
    Not used by endpoints; handy for quickly introspecting the request shape during dev.
    """
    return {"schema_version": req.schema_version, "user_id": req.user_context.user_id}
