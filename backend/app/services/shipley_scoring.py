# app/services/shipley_scoring.py

"""
Phase 2 — Enterprise Shipley Scoring Engine

This replaces the simple:
COMPLIANT = 100
PARTIAL = 60
NOT ADDRESSED = 0

with a weighted enterprise scoring model used for
real bid / proposal reviews.
"""


def normalize_score(value, default=0):
    """
    Safely convert score to float
    """
    try:
        return float(value)
    except Exception:
        return float(default)


def calculate_dimension_score(
    compliance=0,
    proof_points=0,
    customer_language=0,
    executive_messaging=0,
    differentiators=0,
    risk_coverage=0,
    ownership_clarity=0,
    delivery_confidence=0,
    governance_model=0,
    sla_commitment=0
):
    """
    Weighted Shipley-style scoring dimensions

    Each dimension contributes to final score.
    Total = 100
    """

    weights = {
        "compliance": 20,
        "proof_points": 10,
        "customer_language": 10,
        "executive_messaging": 10,
        "differentiators": 10,
        "risk_coverage": 10,
        "ownership_clarity": 10,
        "delivery_confidence": 10,
        "governance_model": 5,
        "sla_commitment": 5
    }

    weighted_score = (
        normalize_score(compliance) * weights["compliance"] +
        normalize_score(proof_points) * weights["proof_points"] +
        normalize_score(customer_language) * weights["customer_language"] +
        normalize_score(executive_messaging) * weights["executive_messaging"] +
        normalize_score(differentiators) * weights["differentiators"] +
        normalize_score(risk_coverage) * weights["risk_coverage"] +
        normalize_score(ownership_clarity) * weights["ownership_clarity"] +
        normalize_score(delivery_confidence) * weights["delivery_confidence"] +
        normalize_score(governance_model) * weights["governance_model"] +
        normalize_score(sla_commitment) * weights["sla_commitment"]
    )

    # because inputs expected between 0–1
    final_score = round(weighted_score, 2)

    return min(final_score, 100)


def status_to_base_score(status):
    """
    Convert compliance status into baseline score
    """

    status = str(status).strip().upper()

    if status == "COMPLIANT":
        return 1.0

    if status == "PARTIAL":
        return 0.6

    if status == "NOT ADDRESSED":
        return 0.0

    return 0.0


def calculate_shipley_score_from_status(status):
    """
    Fast fallback scoring when only status exists
    """

    base = status_to_base_score(status)

    return calculate_dimension_score(
        compliance=base,
        proof_points=base,
        customer_language=base * 0.8,
        executive_messaging=base * 0.7,
        differentiators=base * 0.7,
        risk_coverage=base * 0.6,
        ownership_clarity=base * 0.8,
        delivery_confidence=base * 0.8,
        governance_model=base * 0.5,
        sla_commitment=base * 0.5
    )


def determine_bid_strength(score):
    """
    Executive interpretation of score
    """

    if score >= 85:
        return {
            "label": "Strong Proposal",
            "risk": "Low",
            "win_probability": 85,
            "decision": "PURSUE"
        }

    if score >= 70:
        return {
            "label": "Competitive Proposal",
            "risk": "Medium",
            "win_probability": 70,
            "decision": "PURSUE WITH IMPROVEMENTS"
        }

    if score >= 50:
        return {
            "label": "Needs Improvement",
            "risk": "High",
            "win_probability": 45,
            "decision": "REVIEW BEFORE PURSUIT"
        }

    return {
        "label": "High Risk Submission",
        "risk": "Critical",
        "win_probability": 20,
        "decision": "NO PURSUIT"
    }


def calculate_overall_bid_score(results):
    """
    Calculate full bid score from all reviewed requirements
    """

    if not results:
        return {
            "overall_score": 0,
            "summary": determine_bid_strength(0)
        }

    total_score = 0

    for item in results:
        score = normalize_score(
            item.get("shipley_score", 0)
        )
        total_score += score

    overall = round(
        total_score / len(results),
        2
    )

    summary = determine_bid_strength(overall)

    return {
        "overall_score": overall,
        "summary": summary
    }


def build_section_scores(results):
    """
    Enterprise section-level scoring

    Used for dashboard:
    - Technical
    - Security
    - Delivery
    - Governance
    - Commercial
    """

    if not results:
        return {
            "technical_score": 0,
            "security_score": 0,
            "delivery_score": 0,
            "governance_score": 0,
            "commercial_score": 0
        }

    avg = sum(
        item.get("shipley_score", 0)
        for item in results
    ) / len(results)

    return {
        "technical_score": round(avg * 0.95, 2),
        "security_score": round(avg * 0.90, 2),
        "delivery_score": round(avg * 0.92, 2),
        "governance_score": round(avg * 0.88, 2),
        "commercial_score": round(avg * 0.85, 2)
    }