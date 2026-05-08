# load_kb.py

"""
PHASE 2 — ENTERPRISE KNOWLEDGE BASE LOADER

This script builds / refreshes the RAG knowledge base.

Supported:
- DOCX
- PDF
- TXT
- XLSX
- XLS
- CSV
- Shipley scoring sheets
- PQQ libraries
- Proposal archives
- Delivery frameworks
- CV libraries
- Case studies
- Win themes
- Past performance repositories

Capabilities:
1. Multi-document ingestion
2. Chunking with overlap
3. Semantic embedding generation
4. PostgreSQL + pgvector storage
5. Source traceability
6. Category mapping
7. Enterprise proposal memory layer
"""

import os
import sys
import io

from app.services.rag import embed
from app.db import insert_chunk
from app.utils.extractor import extract_text


# Windows-safe UTF-8 logging
sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer,
    encoding="utf-8"
)


# =====================================================
# CLEAN TEXT
# =====================================================

def clean_text(text):
    """
    Remove bad characters and normalize text
    """

    if not text:
        return ""

    return (
        text.replace("�", "")
        .replace("\x00", "")
        .strip()
    )


# =====================================================
# CHUNKING ENGINE
# =====================================================

def chunk_text(
    text,
    chunk_size_tokens,
    overlap_tokens
):
    """
    Enterprise chunking with overlap.

    Example:
    chunk_size = 2500
    overlap = 500

    Improves:
    - semantic continuity
    - retrieval quality
    - proposal context retention
    """

    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size_tokens

        chunk = " ".join(
            words[start:end]
        )

        if len(chunk.strip()) > 50:
            chunks.append(chunk)

        start = end - overlap_tokens

        if start < 0:
            start = 0

        if start >= len(words):
            break

    return chunks


# =====================================================
# MAIN LOADER
# =====================================================

def load(
    docs_path,
    chunk_size_tokens,
    overlap_tokens
):
    """
    Load all documents from folder
    into PostgreSQL vector DB.
    """

    total_chunks = 0
    total_files = 0

    print("\n================================")
    print("KNOWLEDGE BASE BUILD STARTED")
    print("================================")

    print(
        f"Docs Path: "
        f"{os.path.abspath(docs_path)}"
    )

    print(
        f"Chunk Size: {chunk_size_tokens}"
    )

    print(
        f"Overlap: {overlap_tokens}"
    )

    if not os.path.exists(docs_path):
        print(
            "Knowledge base folder not found"
        )
        return

    # =============================================
    # WALK FOLDER TREE
    # =============================================

    for root, _, files in os.walk(
        docs_path
    ):
        print(f"\nFolder: {root}")

        for file in files:
            total_files += 1

            path = os.path.join(
                root,
                file
            )

            print(
                f"\nProcessing file: {path}"
            )

            try:
                # =================================
                # READ FILE
                # =================================

                with open(
                    path,
                    "rb"
                ) as f:
                    file_bytes = f.read()

                # =================================
                # EXTRACT TEXT
                # =================================

                text = extract_text(
                    file_bytes,
                    file
                )

                text = clean_text(text)

                if not text:
                    print(
                        "Skipped: empty text"
                    )
                    continue

                # =================================
                # CATEGORY
                # =================================

                category = os.path.basename(
                    root
                )

                print(
                    f"Category: {category}"
                )

                # =================================
                # CHUNKING
                # =================================

                chunks = chunk_text(
                    text,
                    chunk_size_tokens,
                    overlap_tokens
                )

                print(
                    f"Chunks created: "
                    f"{len(chunks)}"
                )

                # =================================
                # EMBEDDING + INSERT
                # =================================

                for chunk in chunks:
                    try:
                        embedding = embed(
                            chunk
                        )

                        insert_chunk(
                            content=chunk,
                            embedding=embedding,
                            source_file=file,
                            category="shipley" if "shipley" in file.lower() else "general"
                        )

                        total_chunks += 1

                        print(
                            f"Inserted chunk "
                            f"#{total_chunks}"
                        )

                    except Exception as e:
                        print(
                            f"Insert failed: "
                            f"{str(e)}"
                        )

            except Exception as e:
                print(
                    f"File processing failed: "
                    f"{str(e)}"
                )

    print("\n================================")
    print("KB BUILD COMPLETE")
    print("================================")

    print(
        f"Total files processed: "
        f"{total_files}"
    )

    print(
        f"Total chunks inserted: "
        f"{total_chunks}"
    )

    print(f"Processing file: {path}")
    print(f"Extracted text length: {len(text)}")


# =====================================================
# SCRIPT ENTRY
# =====================================================

if __name__ == "__main__":
    docs_path = sys.argv[1]
    chunk_size_tokens = int(
        sys.argv[2]
    )
    overlap_tokens = int(
        sys.argv[3]
    )

    load(
        docs_path,
        chunk_size_tokens,
        overlap_tokens
    )