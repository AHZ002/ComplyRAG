import os
import fitz  # PyMuPDF
import numpy as np
import faiss
from config.config import DATA_DIR, TOP_K, SIMILARITY_THRESHOLD
from models.embeddings import load_embedding_model, get_embeddings


def load_documents() -> list[str]:
    """Load and chunk all PDF documents from the data directory"""
    try:
        chunks = []
        for fname in os.listdir(DATA_DIR):
            if fname.endswith(".pdf"):
                filepath = os.path.join(DATA_DIR, fname)
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

        print(f"Loaded {len(chunks)} chunks from {DATA_DIR}")
        return chunks

    except Exception as e:
        raise RuntimeError(f"Failed to load documents: {str(e)}")


def build_faiss_index(chunks: list[str], model) -> faiss.IndexFlatIP:
    """Build a FAISS index from document chunks"""
    try:
        embeddings = get_embeddings(chunks, model)
        faiss.normalize_L2(embeddings)

        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)

        print(f"FAISS index built with {index.ntotal} vectors")
        return index

    except Exception as e:
        raise RuntimeError(f"Failed to build FAISS index: {str(e)}")


def retrieve_relevant_chunks(query: str, index: faiss.IndexFlatIP, chunks: list[str], model) -> tuple[str, float]:
    """Retrieve the most relevant chunks for a query"""
    try:
        query_embedding = get_embeddings([query], model)
        faiss.normalize_L2(query_embedding)

        scores, indices = index.search(query_embedding, TOP_K)

        best_score = float(scores[0][0])
        relevant_chunks = [chunks[i] for i in indices[0] if i < len(chunks)]
        context = "\n\n".join(relevant_chunks)

        return context, best_score

    except Exception as e:
        raise RuntimeError(f"Failed to retrieve chunks: {str(e)}")


def is_relevant(score: float) -> bool:
    """Check if the retrieved context meets the similarity threshold"""
    return score >= SIMILARITY_THRESHOLD