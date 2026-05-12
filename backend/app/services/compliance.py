# app/services/compliance.py

import json
import re
import hashlib

from app.services.rag import retrieve
from app.services.shipley import (
    calculate_shipley_score,
    shipley_band,
    build_shipley_guidance
)

from app.utils.llm import call_llm
from app.db import (
    get_cached_result,
    save_cached_result
)


# =====================================================
# JSON EXTRACTION
# =====================================================

def extract_json(text):
    """
    Safely extract JSON returned by LLM.
    Handles:
    - ```json wrappers
    - extra text before/after JSON
    - malformed spacing
    """

    try:
        text = (
            text.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL
        )

        if match:
            return json.loads(match.group())

        raise ValueError("No valid JSON found")

    except Exception as e:
        raise ValueError(
            f"JSON extraction failed: {str(e)}"
        )


# =====================================================
# CACHE HASH
# =====================================================

def generate_hash(req, response):
    """
    Hash for compliance cache
    avoids repeated expensive LLM calls
    """

    raw = req + response
    return hashlib.sha256(
        raw.encode()
    ).hexdigest()


# =====================================================
# EXECUTIVE RECOMMENDATION
# =====================================================

def build_recommendation(status, score):
    """
    Enterprise bid recommendation
    combines:
    - compliance status
    - shipley score
    """

    if status == "COMPLIANT" and score >= 85:
        return (
            "Strong compliant response. Improve executive "
            "messaging, measurable outcomes, and proof points "
            "to maximize win probability."
        )

    if status == "PARTIAL":
        return (
            "Partial compliance detected. Add explicit commitments, "
            "delivery ownership, governance model, SLA language, "
            "and customer-specific value propositions."
        )

    return (
        "Major compliance gap detected. Rewrite response with "
        "direct requirement mapping, clear commitments, evidence, "
        "and strong delivery confidence."
    )


# =====================================================
# MAIN EVALUATION ENGINE
# =====================================================

def evaluate(req, response, top_k=10):
    """
    Phase 2 Enterprise Evaluation Engine

    Performs:
    1. Cache check
    2. RAG evidence retrieval
    3. LLM compliance assessment
    4. True Shipley scoring
    5. Executive guidance generation
    6. Cache persistence
    """

    print("\n===================================")
    print("➡️ Evaluating Requirement")
    print("===================================")
    print(req[:300])

    # =================================================
    # CACHE CHECK
    # =================================================

    requirement_hash = generate_hash(
        req,
        response
    )

    cached = get_cached_result(
        requirement_hash
    )

    if cached:
        print("⚡ CACHE HIT → skipping LLM")
        return cached

    print("❌ CACHE MISS → calling LLM")

    # =================================================
    # RAG RETRIEVAL
    # =================================================

    evidence = retrieve(
        req,
        top_k=top_k
    )

    print(
        f"📄 Evidence retrieved: {len(evidence)} chunks"
    )

    # =================================================
    # STRICT SHIPLEY PROMPT
    # =================================================

    prompt = f"""
You are a strict enterprise bid reviewer using
Shipley methodology and executive proposal review standards.

VERY IMPORTANT RULES:

DO NOT mark COMPLIANT unless:
- requirement is explicitly answered
- commitments are clearly stated
- ownership is clearly defined
- delivery confidence is high
- measurable outcomes exist
- evidence supports the response
- risk mitigation exists where relevant

If answer is vague:
→ return PARTIAL

If answer is weak or missing:
→ return NOT ADDRESSED

You must be VERY strict.

Do NOT be generous.

Return STRICT JSON ONLY.

================================================

Requirement:
{req}

================================================

Vendor Response:
{response[:3000]}

================================================

Knowledge Base Evidence:
{json.dumps(evidence)}

================================================

Return ONLY this JSON:

{{
  "requirement": "{req}",
  "status": "COMPLIANT | PARTIAL | NOT ADDRESSED",
  "confidence": 0,
  "explanation": "short explanation"
}}
"""

    try:
        # =============================================
        # CALL OLLAMA
        # =============================================

        print("🤖 Sending prompt to Ollama...")

        output = call_llm(prompt)

        print("\n===== RAW LLM RESPONSE =====")
        print(output)

        parsed = extract_json(output)

        status = parsed.get(
            "status",
            "NOT ADDRESSED"
        )

        # =================================================
        # TRUE SHIPLEY ENGINE
        # =================================================

        shipley_result = calculate_shipley_score(
            status=status,
            response=response,
            evidence=evidence
        )

        shipley_score = (
            shipley_result["total_score"]
        )

        shipley_details = (
            shipley_result["details"]
        )

        shipley_rating = shipley_band(
            shipley_score
        )

        shipley_guidance = build_shipley_guidance(
            shipley_score,
            shipley_details
        )

        from app.services.shipley import (
            build_shipley_evidence
        )

        shipley_evidence = (
            build_shipley_evidence(
                shipley_details
            )
        )

        # ADD SHIPLEY TRACEABILITY

        evidence.extend(
            shipley_evidence
        )

        recommendation = build_recommendation(
            status,
            shipley_score
        )

        # =============================================
        # FINAL ENRICHED RESULT
        # =============================================

        parsed["shipley_score"] = shipley_score
        parsed["shipley_rating"] = shipley_rating
        parsed["shipley_guidance"] = shipley_guidance
        parsed["shipley_breakdown"] = (
            shipley_details
        )
        parsed["recommendation"] = recommendation
        parsed["evidence"] = evidence

        # =============================================
        # FORCE SHIPLEY TRACEABILITY
        # =============================================

        parsed["evidence"].append({
            "content": (
                "Shipley scoring framework applied "
                "during proposal evaluation."
            ),
            "source": "Shipley_PQR_Guidelines.xlsx",
            "category": "shipley_scoring",
            "confidence": 100,
            "rank": "shipley_reference"
        })

        # =============================================
        # SAVE CACHE
        # =============================================

        save_cached_result(
            requirement_hash,
            req,
            parsed
        )

        print("💾 Saved to cache")

        return parsed

    except Exception as e:
        print("LLM Error:", str(e))

        return {
            "requirement": req,
            "status": "ERROR",
            "confidence": 0,
            "explanation": str(e),
            "shipley_score": 0,
            "shipley_rating": "SYSTEM FAILURE",
            "shipley_guidance": (
                "Evaluation failed due to system issue."
            ),
            "recommendation": (
                "System failure during compliance review."
            ),
            "evidence": evidence
        }