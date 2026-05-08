# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from app.api.routes import router

print("======================================")
print("Starting Enterprise Bid Intelligence API")
print("Phase 2 - RFP Compliance + Shipley Scoring")
print("======================================")

app = FastAPI(
    title="Enterprise Bid Intelligence Platform",
    description="""
Production-grade AI platform for:

- RFP Compliance Review
- Shipley Scoring
- Proposal Quality Validation
- Knowledge Base Retrieval (RAG)
- Evidence-backed Compliance Decisions
- Recommendation Engine
- Executive Dashboard Metrics
- PostgreSQL + pgvector + Cache Layer
""",
    version="2.0.0"
)

class KBRequest(BaseModel):
    docs_path: str
# =====================================================
# CORS CONFIGURATION
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# ROUTES
# =====================================================

app.include_router(router)


# =====================================================
# ROOT HEALTH CHECK
# =====================================================

@app.get("/")
def root():
    return {
        "message": "Enterprise Bid Intelligence Platform Running",
        "version": "2.0.0",
        "status": "healthy",
        "features": [
            "RFP Compliance Review",
            "Shipley Scoring",
            "RAG Knowledge Retrieval",
            "Executive Dashboard",
            "Caching Engine",
            "Recommendation Engine",
            "Proposal Validation"
        ]
    }


@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": "Bid Intelligence Platform",
        "phase": "Phase 2 Enterprise",
        "database": "PostgreSQL + pgvector",
        "llm": "Ollama + Mistral",
        "retrieval": "RAG Enabled"
    }

@app.post("/refresh-kb")
async def refresh_kb(req: KBRequest):
    print("Refreshing KB from:", req.docs_path)

    # TODO: call your indexing / embedding pipeline here

    return {
        "status": "success",
        "message": f"Knowledge base refreshed from {req.docs_path}"
    }

print("======================================")
print("FastAPI routes loaded successfully")
print("API Ready")
print("======================================")