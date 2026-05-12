# app/api/routes.py

from fastapi import (
    APIRouter,
    UploadFile,
    Form,
    File
)

import sys
import subprocess

from app.services.compliance import evaluate
from app.utils.extractor import extract_text


router = APIRouter()


# =========================================================
# HEALTH CHECK
# =========================================================

@router.get("/")
async def root():
    return {
        "message": "Enterprise Bid Intelligence Platform Running"
    }


# =========================================================
# BUILD / REFRESH KNOWLEDGE BASE
# =========================================================

@router.post("/build-refresh-index")
async def build_refresh_index(
    docs_path: str = Form(...),
    chunk_size_tokens: int = Form(...),
    overlap_tokens: int = Form(...)
):
    """
    Rebuild knowledge base from local folder.

    Supports:
    - DOCX
    - PDF
    - TXT
    - XLSX
    - XLS

    This executes:
    load_kb.py

    and refreshes PostgreSQL + pgvector store
    """
    import os

    print("\n======================================")
    print("BUILD / REFRESH KNOWLEDGE BASE")
    print("======================================")

    print(f"Docs Path: {docs_path}")
    print(f"Chunk Size: {chunk_size_tokens}")
    print(f"Overlap: {overlap_tokens}")

    # ✅ Validate path first
    if not os.path.exists(docs_path):
        return {
            "error": f"Docs path does NOT exist: {docs_path}"
        }

    try:
        result = subprocess.run(
            [
                sys.executable,
                "load_kb.py",
                docs_path,
                str(chunk_size_tokens),
                str(overlap_tokens)
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print("Knowledge Base refreshed successfully")
        print("\n===== STDOUT =====")
        print(result.stdout)

        print("\n===== STDERR (WARNINGS / ERRORS) =====")
        print(result.stderr)


        return {
            "message": "Knowledge Base refreshed successfully",
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except subprocess.CalledProcessError as e:
        print("KB Refresh Failed")
        print(e.stderr)

        return {
            "error": (
                f"Error executing load_kb.py: "
                f"{e.stderr}"
            )
        }


# =========================================================
# COMPLIANCE REVIEW
# =========================================================

@router.post("/review")
async def review(
    rfp: UploadFile = File(None),
    response: UploadFile = File(None),

    rfp_text: str = Form(None),
    response_text: str = Form(None),

    chunk_size_tokens: int = Form(2500),
    overlap_tokens: int = Form(500),
    top_k_chunks: int = Form(10)
):
    """
    Enterprise Compliance Review API

    Accepts:
    - RFP file OR text
    - Response file OR text

    Returns:
    - compliance results
    - Shipley score
    - executive guidance
    - recommendations
    - evidence source traceability
    """

    print("\n======================================")
    print("REVIEW API CALLED")
    print("======================================")

    try:
        # =================================================
        # HANDLE RFP INPUT
        # =================================================

        if rfp:
            print(
                f"RFP file uploaded: "
                f"{rfp.filename}"
            )

            rfp_bytes = await rfp.read()

            rfp_text = extract_text(
                rfp_bytes,
                rfp.filename
            )
            print(
                f"sks: RFP_TEXT with Uplaod: "
                f"{rfp_text}"
            )

        elif rfp_text:
            print(
                "RFP provided via text input"
            )

        else:
            return {
                "results": [],
                "error": (
                    "Please provide "
                    "RFP file or RFP text"
                )
            }

        # =================================================
        # HANDLE RESPONSE INPUT
        # =================================================

        if response:
            print(
                f"Response file uploaded: "
                f"{response.filename}"
            )

            response_bytes = await response.read()

            response_text = extract_text(
                response_bytes,
                response.filename
            )

        elif response_text:
            print(
                "Response provided via text input"
            )

        else:
            return {
                "results": [],
                "error": (
                    "Please provide "
                    "Response file or Response text"
                )
            }

        # =================================================
        # LOGGING
        # =================================================

        print(
            f"RFP text length: "
            f"{len(rfp_text)}"
        )

        print(
            f"Response text length: "
            f"{len(response_text)}"
        )

        print(
            f"Chunk Size: "
            f"{chunk_size_tokens}"
        )

        print(
            f"Overlap: "
            f"{overlap_tokens}"
        )

        print(
            f"Top K Chunks: "
            f"{top_k_chunks}"
        )

        # =================================================
        # REQUIREMENT EXTRACTION
        # =================================================

        requirements = [
            line.strip()
            for line in rfp_text.split("\n")
            if len(line.strip()) > 30
        ][:15]

        print(
            f"Requirements found: "
            f"{len(requirements)}"
        )

        if not requirements:
            return {
                "results": [],
                "error": (
                    "No valid requirements "
                    "found in RFP"
                )
            }

        # =================================================
        # EVALUATION LOOP
        # =================================================

        results = []

        for index, req in enumerate(
            requirements,
            start=1
        ):
            print(
                f"\nEvaluating Requirement "
                f"{index}/{len(requirements)}"
            )

            print(req[:300])

            result = evaluate(
                req=req,
                response=response_text,
                top_k=top_k_chunks
            )

            results.append(result)

        # =================================================
        # EXECUTIVE SUMMARY
        # =================================================

        total = len(results)

        compliant_count = len([
            r for r in results
            if r.get("status") == "COMPLIANT"
        ])

        partial_count = len([
            r for r in results
            if r.get("status") == "PARTIAL"
        ])

        not_addressed_count = len([
            r for r in results
            if r.get("status") == "NOT ADDRESSED"
        ])

        avg_shipley_score = round(
            sum(
                r.get("shipley_score", 0)
                for r in results
            ) / total,
            1
        ) if total else 0

        executive_summary = {
            "total_requirements": total,
            "compliant": compliant_count,
            "partial": partial_count,
            "not_addressed": not_addressed_count,
            "average_shipley_score": avg_shipley_score
        }

        print("\n======================================")
        print("FINAL REVIEW COMPLETE")
        print("======================================")
        print(executive_summary)

        return {
            "executive_summary": executive_summary,
            "results": results
        }

    except Exception as e:
        print("\nERROR in /review")
        print(str(e))

        return {
            "results": [],
            "error": str(e)
        }