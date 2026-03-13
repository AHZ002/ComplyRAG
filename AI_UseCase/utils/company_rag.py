import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import fitz
import numpy as np
import faiss
from config.config import COMPANY_DATA_DIR, TOP_K
from models.embeddings import get_embeddings


def load_company_documents() -> list[str]:
    """Load and chunk all PDF documents from the company data directory"""
    try:
        chunks = []
        if not os.path.exists(COMPANY_DATA_DIR):
            return chunks

        for fname in os.listdir(COMPANY_DATA_DIR):
            if fname.endswith(".pdf"):
                filepath = os.path.join(COMPANY_DATA_DIR, fname)
                doc = fitz.open(filepath)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()

                # Chunk by words with overlap
                words = text.split()
                chunk_size = 200
                overlap = 20

                for i in range(0, len(words), chunk_size - overlap):
                    chunk = " ".join(words[i:i + chunk_size])
                    if len(chunk.strip()) > 50:
                        chunks.append(chunk)

        print(f"Loaded {len(chunks)} company policy chunks from {COMPANY_DATA_DIR}")
        return chunks

    except Exception as e:
        raise RuntimeError(f"Failed to load company documents: {str(e)}")


def build_company_faiss_index(chunks: list[str], model) -> faiss.IndexFlatIP:
    """Build a FAISS index from company document chunks"""
    try:
        embeddings = get_embeddings(chunks, model)
        faiss.normalize_L2(embeddings)

        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)

        print(f"Company FAISS index built with {index.ntotal} vectors")
        return index

    except Exception as e:
        raise RuntimeError(f"Failed to build company FAISS index: {str(e)}")


def retrieve_company_chunks(query: str, index: faiss.IndexFlatIP, chunks: list[str], model) -> str:
    """Retrieve the most relevant chunks from company documents for a query"""
    try:
        query_embedding = get_embeddings([query], model)
        faiss.normalize_L2(query_embedding)

        scores, indices = index.search(query_embedding, TOP_K)

        relevant_chunks = [chunks[i] for i in indices[0] if i < len(chunks)]
        context = "\n\n".join(relevant_chunks)

        return context

    except Exception as e:
        raise RuntimeError(f"Failed to retrieve company chunks: {str(e)}")


def is_compliance_query(query: str) -> bool:
    """
    Detect if the user is asking a compliance gap analysis question
    that requires comparing company policy against a framework
    """
    query_lower = query.lower()
    compliance_keywords = [
        "our policy", "our company", "our organization", "our organisation",
        "company policy", "compliant", "compliance", "gap", "gaps",
        "missing", "does our", "is our", "are we", "do we comply",
        "techcorp", "align", "alignment", "meet the", "satisfy",
        "adhere", "conform", "requirement", "against"
    ]
    return any(keyword in query_lower for keyword in compliance_keywords)