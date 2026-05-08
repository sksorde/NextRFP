# app/services/rag.py

"""
PHASE 2 — ENTERPRISE RAG ENGINE

Capabilities:
1. Semantic retrieval using PostgreSQL + pgvector
2. Source traceability
3. Category-aware retrieval
4. Confidence-driven ranking
5. Hybrid enterprise retrieval preparation
6. Shipley scoring evidence support
7. Proposal reviewer traceability layer

This is no longer basic RAG.
This becomes enterprise-grade retrieval.
"""

from sentence_transformers import SentenceTransformer
from app.db import search_chunks

model = None


# =====================================================
# LOAD EMBEDDING MODEL
# =====================================================

def get_model():
    """
    Lazy-load embedding model once only.

    Using:
    all-MiniLM-L6-v2

    Fast + reliable for enterprise retrieval.
    """

    global model

    if model is None:
        print("\n================================")
        print("Loading embedding model...")
        print("================================")

        model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print(
            "Embedding model loaded successfully"
        )

    return model


# =====================================================
# CREATE EMBEDDING
# =====================================================

def embed(text):
    """
    Generate vector embedding
    for semantic similarity search.
    """

    model = get_model()

    vector = model.encode(
        text
    ).tolist()

    return str(vector)


# =====================================================
# NORMALIZE SOURCE CONFIDENCE
# =====================================================

def calculate_confidence(rank_position):
    """
    Simple enterprise confidence logic.

    Top result → highest confidence

    Can be upgraded later to:
    hybrid search + reranker
    """

    if rank_position == 1:
        return 95

    if rank_position <= 3:
        return 85

    if rank_position <= 5:
        return 75

    if rank_position <= 10:
        return 65

    return 50


# =====================================================
# ENTERPRISE RETRIEVAL ENGINE
# =====================================================

def retrieve(query, top_k=10):
    """
    Retrieve most relevant chunks from:

    PostgreSQL + pgvector

    Features:
    - semantic similarity
    - source file visibility
    - category traceability
    - confidence score
    - executive review evidence

    Returns:
    [
        {
            content,
            source,
            category,
            confidence
        }
    ]
    """

    print("\n================================")
    print("RAG RETRIEVAL STARTED")
    print("================================")

    print(f"Query: {query[:300]}")
    print(f"Top K Requested: {top_k}")

    # =============================================
    # QUERY EMBEDDING
    # =============================================

    query_embedding = embed(query)

    # =============================================
    # VECTOR SEARCH
    # =============================================

    rows = search_chunks(
        query_embedding,
        k=top_k * 2
    )

    print(
        f"Retrieved rows from pgvector: "
        f"{len(rows)}"
    )

    results = []

    for index, row in enumerate(
        rows,
        start=1
    ):
        content = row[0]
        source = row[1]
        category = row[2]

        # 🔥 BOOST SHIPLEY FILES
        boost = 10 if "shipley" in (source or "").lower() else 0

        confidence = calculate_confidence(
            index
        ) + boost

        results.append(
            {
                "content": content,
                "source": source,
                "category": category,
                "confidence": confidence,
                "rank": index
            }
        )

    shipley_rows = [
        r for r in rows
        if r[2] == "shipley_scoring"
    ]

    if not shipley_rows:
        print("Injecting Shipley reference into evidence")

        # fetch 2 shipley chunks manually
        extra = search_chunks(embed("shipley scoring framework"), k=3)

        for r in extra:
            if r[2] == "shipley_scoring":
                results.append({
                    "content": r[0],
                    "source": r[1],
                    "category": r[2],
                    "confidence": 90,
                    "rank": "shipley_ref"
                })

    
    print("\n===== RETRIEVED EVIDENCE =====")

    for item in results[:5]:
        print(
            f"[Rank {item['rank']}] "
            f"{item['source']} | "
            f"{item['category']} | "
            f"Confidence: {item['confidence']}%"
        )

    print("================================")

    return sorted(results, key=lambda x: -x["confidence"])[:top_k]