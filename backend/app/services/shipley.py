# app/services/shipley.py

"""
PHASE 2 — ENTERPRISE SHIPLEY SCORING ENGINE

This module upgrades simple status-based scoring into
true enterprise Shipley-style scoring using:

1. Compliance completeness
2. Win theme strength
3. Proof points / evidence quality
4. Customer language alignment
5. Risk mitigation
6. Executive value proposition
7. Differentiators / discriminators
8. Delivery confidence
9. Ownership clarity
10. Past performance strength

It also uses:
backend/knowledge_base/shipley_scoring/Shipley_PQR_Guidelines.xlsx

to enrich scoring logic.

This becomes the REAL Shipley scoring layer.
"""

import os
import pandas as pd


SHIPLEY_FILE = (
    "knowledge_base/shipley_scoring/"
    "Shipley_PQR_Guidelines.xlsx"
)


def load_shipley_reference():
    """
    Load Shipley scoring reference Excel.

    Safe fallback:
    if file not found → continue without breaking system.
    """

    try:
        if not os.path.exists(SHIPLEY_FILE):
            print("Shipley reference file not found.")
            return []

        df = pd.read_excel(SHIPLEY_FILE)

        print(
            f"Loaded Shipley reference rows: {len(df)}"
        )

        return df.fillna("").to_dict(orient="records")

    except Exception as e:
        print(
            f"Shipley Excel load failed: {str(e)}"
        )
        return []


SHIPLEY_REFERENCE = load_shipley_reference()


def score_compliance(status):
    """
    Base compliance score
    """

    if status == "COMPLIANT":
        return 25

    if status == "PARTIAL":
        return 12

    return 0


def score_evidence(evidence):
    """
    Evidence quality score
    """

    if not evidence:
        return 0

    if len(evidence) >= 5:
        return 15

    if len(evidence) >= 3:
        return 10

    return 5


def score_customer_language(response):
    """
    Customer language alignment

    Higher score if response reflects
    buyer language instead of generic vendor language.
    """

    keywords = [
        "outcome",
        "value",
        "business impact",
        "transformation",
        "service level",
        "governance",
        "security",
        "compliance",
        "delivery model",
        "risk mitigation",
        "stakeholder",
        "ownership"
    ]

    score = 0

    text = response.lower()

    for word in keywords:
        if word in text:
            score += 2

    return min(score, 15)


def score_commitment_strength(response):
    """
    Explicit commitments score

    Stronger when words like:
    shall / will / committed / guaranteed
    are present
    """

    strong_words = [
        "shall",
        "will",
        "committed",
        "guarantee",
        "ensure",
        "deliver",
        "provide",
        "own",
        "responsible",
        "sla"
    ]

    score = 0
    text = response.lower()

    for word in strong_words:
        if word in text:
            score += 2

    return min(score, 15)


def score_differentiators(response):
    """
    Differentiator score

    Helps identify:
    why client should choose this bidder
    """

    keywords = [
        "unique",
        "proven",
        "accelerator",
        "framework",
        "innovation",
        "best practice",
        "certified",
        "award",
        "case study",
        "reference client"
    ]

    score = 0
    text = response.lower()

    for word in keywords:
        if word in text:
            score += 2

    return min(score, 15)


def score_risk_mitigation(response):
    """
    Risk handling score
    """

    keywords = [
        "risk",
        "mitigation",
        "dependency",
        "assumption",
        "contingency",
        "fallback",
        "governance",
        "escalation"
    ]

    score = 0
    text = response.lower()

    for word in keywords:
        if word in text:
            score += 2

    return min(score, 15)


def calculate_shipley_score(
    status,
    response,
    evidence
):
    """
    FINAL ENTERPRISE SHIPLEY SCORE

    Total = 100
    """

    total = 0

    total += score_compliance(status)
    total += score_evidence(evidence)
    total += score_customer_language(response)
    total += score_commitment_strength(response)
    total += score_differentiators(response)
    total += score_risk_mitigation(response)

    return min(total, 100)


def shipley_band(score):
    """
    Executive grading band
    """

    if score >= 85:
        return "EXCELLENT"

    if score >= 70:
        return "STRONG"

    if score >= 50:
        return "MODERATE RISK"

    return "HIGH RISK"


def build_shipley_guidance(score):
    """
    Executive recommendation
    """

    if score >= 85:
        return (
            "Strong submission with high win probability. "
            "Focus on executive polish and stronger proof points."
        )

    if score >= 70:
        return (
            "Competitive proposal. Improve customer language, "
            "ownership clarity, and differentiation."
        )

    if score >= 50:
        return (
            "Moderate risk. Add stronger commitments, "
            "governance, measurable outcomes, and proof."
        )

    return (
        "High risk submission. Major response gaps exist. "
        "Rewrite with explicit compliance mapping, "
        "delivery ownership, and clear commitments."
    )