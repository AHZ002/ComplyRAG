import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sentence_transformers import SentenceTransformer

# Load the embedding model
_model = None

def load_embedding_model():
    """Load and return the sentence transformer embedding model"""
    try:
        global _model
        if _model is None:
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        return _model
    except Exception as e:
        raise RuntimeError(f"Failed to load embedding model: {str(e)}")

def get_embeddings(texts: list[str], model: SentenceTransformer) -> list:
    """Generate embeddings for a list of texts"""
    try:
        embeddings = model.encode(texts, show_progress_bar=False)
        return embeddings
    except Exception as e:
        raise RuntimeError(f"Failed to generate embeddings: {str(e)}")