import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

# Model settings
GROQ_MODEL = "llama-3.1-70b-versatile"

# RAG settings
SIMILARITY_THRESHOLD = 0.45
TOP_K = 3

# Data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")