from sentence_transformers import SentenceTransformer
import numpy as np

# Global model instance to avoid reloading
_model = None


def load_embedding_model() -> SentenceTransformer:
    """Load and return the sentence transformer embedding model (singleton)"""
    try:
        global _model
        if _model is None:
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        return _model
    except Exception as e:
        raise RuntimeError(f"Failed to load embedding model: {str(e)}")


def get_embeddings(texts: list[str], model: SentenceTransformer) -> np.ndarray:
    """Generate embeddings for a list of texts"""
    try:
        embeddings = model.encode(texts, show_progress_bar=False)
        return np.array(embeddings).astype("float32")
    except Exception as e:
        raise RuntimeError(f"Failed to generate embeddings: {str(e)}")