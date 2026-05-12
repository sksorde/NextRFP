# ============================================================
# TRUE ENTERPRISE SHIPLEY RUBRIC ENGINE
# ============================================================

import os
import pandas as pd
import math

def safe_float(value, default=0.0):
    """
    Prevent NaN propagation from Excel.
    """

    try:
        v = float(value)

        if math.isnan(v):
            return default

        return v

    except:
        return default


SHIPLEY_FILE = (
    "knowledge_base/shipley_scoring/"
    "Shipley_PQR_Guidelines.xlsx"
)


# ============================================================
# LOAD RUBRIC
# ============================================================


def load_shipley_reference():
    """
    Load actual Shipley rubric sheet.
    """

    try:
        if not os.path.exists(SHIPLEY_FILE):
            print("Shipley rubric file missing")
            return []

        df = pd.read_excel(
            SHIPLEY_FILE,
            sheet_name="Combined Response Evaluation"
        )

        df.columns = [
            str(c).strip()
            for c in df.columns
        ]

        rows = []

        for _, row in df.iterrows():

            criterion = str(
                row.iloc[0]
            ).strip()

            weight = safe_float(row.iloc[1])

            if weight <= 0:
                continue

            if (
                not criterion
                or criterion == "nan"
                or criterion.startswith(
                    "DRAFT PROPOSAL"
                )
            ):
                continue

            rows.append({
                "criterion": criterion,
                "weight": safe_float(row.iloc[1]),
                "excellent": str(row.iloc[3]),
                "good": str(row.iloc[4]),
                "acceptable": str(row.iloc[5]),
                "below": str(row.iloc[6]),
                "poor": str(row.iloc[7]),
                "unacceptable": str(row.iloc[8])
            })

        print(
            f"Loaded Shipley rubric rows: {len(rows)}"
        )

        return rows

    except Exception as e:
        print(
            f"Shipley rubric load failed: {str(e)}"
        )
        return []


SHIPLEY_REFERENCE = load_shipley_reference()


# ============================================================
# TEXT MATCHING
# ============================================================


def calculate_match_score(
    response,
    rubric_text
):
    """
    Simple semantic-style keyword overlap.

    Can later be upgraded to:
    - embeddings
    - reranker
    - LLM scoring
    """

    if not response:
        return 0

    if not rubric_text:
        return 0

    response = response.lower()

    words = [
        w.strip(".,:;()[]")
        for w in rubric_text.lower().split()
        if len(w) > 4
    ]

    if not words:
        return 0

    matched = 0

    for word in set(words):
        if word in response:
            matched += 1

    return matched / len(set(words))


# ============================================================
# DETERMINE RUBRIC LEVEL
# ============================================================


def evaluate_criterion(
    criterion,
    response,
    evidence
):
    """
    Evaluate response against rubric levels.
    """

    levels = [
        (5, "excellent"),
        (4, "good"),
        (3, "acceptable"),
        (2, "below"),
        (1, "poor"),
        (0, "unacceptable")
    ]

    best_level = 0
    best_score = 0
    best_name = "UNACCEPTABLE"

    for score, key in levels:

        rubric_text = criterion.get(key, "")

        similarity = calculate_match_score(
            response,
            rubric_text
        )

        weighted = similarity * score

        if weighted > best_score:
            best_score = weighted
            best_level = score
            best_name = key.upper()

    max_weight = safe_float(
        criterion["weight"],
        0
    )

    normalized = (
        best_level / 5
    ) * max_weight

    return {
        "criterion": criterion["criterion"],
        "level": best_name,
        "maturity_score": best_level,
        "weight": max_weight,
        "weighted_score": round(normalized, 2),
        "explanation": (
            f"Matched rubric level: {best_name}"
        )
    }


# ============================================================
# MAIN ENGINE
# ============================================================


def calculate_shipley_score(
    status,
    response,
    evidence
):
    """
    TRUE SHIPLEY RUBRIC EVALUATION ENGINE.
    """

    total = 0

    breakdown = []

    for criterion in SHIPLEY_REFERENCE:

        result = evaluate_criterion(
            criterion,
            response,
            evidence
        )

        breakdown.append(result)

        total += result[
            "weighted_score"
        ]

    # =====================================================
    # COMPLIANCE BOOST
    # =====================================================

    if status == "COMPLIANT":
        total += 5

    elif status == "PARTIAL":
        total += 2

    if math.isnan(total):
        total = 0

    final_score = min(
        round(total, 2),
        100
    )

    return {
        "total_score": final_score,
        "details": breakdown
    }


# ============================================================
# EXECUTIVE BAND
# ============================================================


def shipley_band(score):

    if score >= 90:
        return "OUTSTANDING"

    if score >= 80:
        return "EXCELLENT"

    if score >= 70:
        return "STRONG"

    if score >= 50:
        return "MODERATE RISK"

    return "HIGH RISK"


# ============================================================
# GUIDANCE
# ============================================================


def build_shipley_guidance(
    score,
    details
):

    weak = []

    for d in details:

        pct = (
            d["weighted_score"]
            / d["weight"]
        ) * 100

        if pct < 50:
            weak.append(
                d["criterion"]
            )

    if not weak:
        return (
            "Proposal demonstrates strong "
            "Shipley maturity across all "
            "evaluation dimensions."
        )

    return (
        "Improve proposal maturity in: "
        + ", ".join(weak)
    )


# ============================================================
# TRACEABILITY EVIDENCE
# ============================================================


def build_shipley_evidence(details):

    evidence = []

    for item in details:

        evidence.append({
            "content": (
                f"Shipley criterion evaluated: "
                f"{item['criterion']} | "
                f"Level: {item['level']} | "
                f"Weighted Score: "
                f"{item['weighted_score']}"
            ),
            "source": "Shipley_PQR_Guidelines.xlsx",
            "category": "shipley_scoring",
            "confidence": 95,
            "rank": "shipley_rubric"
        })

    return evidence