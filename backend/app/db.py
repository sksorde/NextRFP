import psycopg2
import json
from datetime import datetime


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_conn():
    return psycopg2.connect(
        dbname="bid",
        user="postgres",
        password="admin",
        host="localhost",
        port="5432"
    )


# =====================================================
# SCHEMA INITIALIZATION
# =====================================================

def init_db():
    """
    Creates all enterprise-grade tables required for
    Bid Intelligence Platform Phase 2
    """

    conn = get_conn()
    cur = conn.cursor()

    # ---------------------------------------------
    # Enable pgvector
    # ---------------------------------------------

    cur.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
    """)

    # ---------------------------------------------
    # Knowledge Base Chunks
    # ---------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS kb_chunks (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            embedding VECTOR(384),
            source_file TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # ---------------------------------------------
    # Compliance Cache
    # ---------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS compliance_cache (
            id SERIAL PRIMARY KEY,
            requirement_hash TEXT UNIQUE,
            requirement TEXT,
            result JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # ---------------------------------------------
    # Bid Reviews Master Table
    # ---------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bid_reviews (
            id SERIAL PRIMARY KEY,
            bid_name TEXT NOT NULL,
            customer_name TEXT,
            submission_deadline TEXT,
            review_status TEXT DEFAULT 'IN_PROGRESS',
            overall_score FLOAT DEFAULT 0,
            win_probability FLOAT DEFAULT 0,
            pursue_decision TEXT DEFAULT 'PENDING',
            created_by TEXT DEFAULT 'system',
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # ---------------------------------------------
    # Requirement-wise Review Results
    # ---------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS review_results (
            id SERIAL PRIMARY KEY,
            bid_review_id INTEGER REFERENCES bid_reviews(id) ON DELETE CASCADE,
            requirement TEXT,
            status TEXT,
            confidence FLOAT,
            shipley_score FLOAT,
            explanation TEXT,
            recommendation TEXT,
            response_excerpt TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # ---------------------------------------------
    # Evidence Mapping
    # ---------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS review_evidence (
            id SERIAL PRIMARY KEY,
            review_result_id INTEGER REFERENCES review_results(id) ON DELETE CASCADE,
            source_file TEXT,
            category TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # ---------------------------------------------
    # Executive Summary
    # ---------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS executive_summary (
            id SERIAL PRIMARY KEY,
            bid_review_id INTEGER REFERENCES bid_reviews(id) ON DELETE CASCADE,
            summary TEXT,
            strengths TEXT,
            weaknesses TEXT,
            red_flags TEXT,
            recommendation TEXT,
            pursue_no_pursue TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # ---------------------------------------------
    # Section-wise Scoring Matrix
    # ---------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS scoring_matrix (
            id SERIAL PRIMARY KEY,
            bid_review_id INTEGER REFERENCES bid_reviews(id) ON DELETE CASCADE,
            compliance_score FLOAT DEFAULT 0,
            technical_score FLOAT DEFAULT 0,
            security_score FLOAT DEFAULT 0,
            delivery_score FLOAT DEFAULT 0,
            governance_score FLOAT DEFAULT 0,
            commercial_score FLOAT DEFAULT 0,
            transition_score FLOAT DEFAULT 0,
            innovation_score FLOAT DEFAULT 0,
            customer_alignment_score FLOAT DEFAULT 0,
            executive_messaging_score FLOAT DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # ---------------------------------------------
    # Reviewer Comments
    # ---------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviewer_comments (
            id SERIAL PRIMARY KEY,
            bid_review_id INTEGER REFERENCES bid_reviews(id) ON DELETE CASCADE,
            reviewer_name TEXT,
            review_stage TEXT,
            comment TEXT,
            severity TEXT DEFAULT 'MEDIUM',
            approval_status TEXT DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # ---------------------------------------------
    # Review History / Audit Trail
    # ---------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS review_history (
            id SERIAL PRIMARY KEY,
            bid_review_id INTEGER REFERENCES bid_reviews(id) ON DELETE CASCADE,
            action_type TEXT,
            action_by TEXT,
            previous_score FLOAT,
            new_score FLOAT,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    # ---------------------------------------------
    # Approval Workflow
    # ---------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS approval_workflow (
            id SERIAL PRIMARY KEY,
            bid_review_id INTEGER REFERENCES bid_reviews(id) ON DELETE CASCADE,
            review_stage TEXT,
            approver_name TEXT,
            approval_status TEXT DEFAULT 'PENDING',
            approval_comments TEXT,
            approved_at TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

    print("Enterprise DB schema initialized successfully")


# =====================================================
# KNOWLEDGE BASE FUNCTIONS
# =====================================================

def insert_chunk(content, embedding, source_file, category):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO kb_chunks
        (content, embedding, source_file, category)
        VALUES (%s, %s, %s, %s)
    """, (
        content,
        embedding,
        source_file,
        category
    ))

    conn.commit()
    cur.close()
    conn.close()


def search_chunks(query_embedding, k=10):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            content,
            source_file,
            category
        FROM kb_chunks
        ORDER BY embedding <-> %s::vector
        LIMIT %s
    """, (
        query_embedding,
        k
    ))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


# =====================================================
# CACHE FUNCTIONS
# =====================================================

def get_cached_result(requirement_hash):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT result
        FROM compliance_cache
        WHERE requirement_hash = %s
    """, (requirement_hash,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return row[0]

    return None


def save_cached_result(requirement_hash, requirement, result):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO compliance_cache
        (
            requirement_hash,
            requirement,
            result
        )
        VALUES (%s, %s, %s)
        ON CONFLICT (requirement_hash)
        DO NOTHING
    """, (
        requirement_hash,
        requirement,
        json.dumps(result)
    ))

    conn.commit()
    cur.close()
    conn.close()


# =====================================================
# BID REVIEW MASTER FUNCTIONS
# =====================================================

def create_bid_review(
    bid_name,
    customer_name,
    submission_deadline,
    created_by="system"
):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO bid_reviews
        (
            bid_name,
            customer_name,
            submission_deadline,
            created_by
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (
        bid_name,
        customer_name,
        submission_deadline,
        created_by
    ))

    review_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return review_id


def update_bid_review_score(
    bid_review_id,
    overall_score,
    win_probability,
    pursue_decision
):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE bid_reviews
        SET
            overall_score = %s,
            win_probability = %s,
            pursue_decision = %s,
            updated_at = NOW()
        WHERE id = %s
    """, (
        overall_score,
        win_probability,
        pursue_decision,
        bid_review_id
    ))

    conn.commit()
    cur.close()
    conn.close()


# =====================================================
# REVIEW RESULT STORAGE
# =====================================================

def save_review_result(
    bid_review_id,
    result
):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO review_results
        (
            bid_review_id,
            requirement,
            status,
            confidence,
            shipley_score,
            explanation,
            recommendation,
            response_excerpt
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        bid_review_id,
        result.get("requirement"),
        result.get("status"),
        result.get("confidence"),
        result.get("shipley_score"),
        result.get("explanation"),
        result.get("recommendation"),
        result.get("response_excerpt", "")
    ))

    review_result_id = cur.fetchone()[0]

    for ev in result.get("evidence", []):
        cur.execute("""
            INSERT INTO review_evidence
            (
                review_result_id,
                source_file,
                category,
                content
            )
            VALUES (%s, %s, %s, %s)
        """, (
            review_result_id,
            ev.get("source"),
            ev.get("category"),
            ev.get("content")
        ))

    conn.commit()
    cur.close()
    conn.close()

    return review_result_id


# =====================================================
# STARTUP
# =====================================================

if __name__ == "__main__":
    init_db()