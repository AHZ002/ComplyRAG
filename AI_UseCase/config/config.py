import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

# Model settings
GROQ_MODEL = "llama-3.3-70b-versatile"

# RAG settings
SIMILARITY_THRESHOLD = 0.55
TOP_K = 3

# Data directories
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
COMPANY_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "company")