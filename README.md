# 🛡️ ComplyRAG — AI-Powered Compliance Assistant

> An intelligent chatbot that answers questions about compliance frameworks like NIST Cybersecurity Framework, ISO 27001, and SOC 2 or any other complaince framework using RAG over official documentation, company policy gap analysis, and live web search fallback.

**Live Demo:** [https://complyrag.streamlit.app/](https://complyrag.streamlit.app/)

---

## 📌 Overview

ComplyRAG is built as part of the NeoStats AI Engineer assignment. It demonstrates a production-ready dual-index RAG pipeline where:

- Queries about **NIST CSF** are answered from local documentation using semantic search
- Queries about **ISO 27001, SOC 2, or any other compliance topic** fall back to live Tavily web search automatically
- Queries about **company policy compliance** trigger a gap analysis by comparing company documents against compliance frameworks
- Users can toggle between **Concise** and **Detailed** response modes
- Every response includes **source attribution** — showing whether the answer came from local documents, gap analysis, or the web

---

## 🏗️ Project Structure
```
AI_UseCase/
├── config/
│   ├── __init__.py
│   └── config.py               # API keys, RAG settings, model config
│
├── models/
│   ├── __init__.py
│   ├── llm.py                  # Groq LLM initialization + response generation
│   └── embeddings.py           # Sentence-transformer model loader
│
├── utils/
│   ├── __init__.py
│   ├── rag.py                  # PDF loading, chunking, FAISS index, retrieval
│   ├── search.py               # Tavily web search wrapper
│   └── company_rag.py          # Company policy FAISS index + compliance query detection
│
├── data/
│   ├── NIST.CSWP.04162018.pdf      # NIST Cybersecurity Framework document
│   └── company/
│       └── TechCorp_IT_Security_Policy.pdf   # Sample company security policy
│
├── app.py                      # Main Streamlit UI and pipeline orchestration
└── requirements.txt
```

---

## ⚙️ How It Works
```
User Query
    ↓
Is this a compliance/gap analysis query?
    ├── YES → Retrieve from Company Policy Index + Framework Index
    │             ↓
    │         Framework score ≥ 0.55?
    │             ├── YES → Use NIST CSF document context
    │             └── NO  → Use Tavily web search for framework context
    │             ↓
    │         LLM performs gap analysis → Compliant / Gaps / Recommendations
    │
    └── NO  → FAISS Semantic Search (NIST CSF document)
                  ↓
              Similarity Score ≥ 0.55?
                  ├── YES → Use RAG context → Groq LLM → Response (📄 Local Source)
                  └── NO  → Tavily Web Search → Groq LLM → Response (🌐 Web Source)
```

---

## 🧰 Tech Stack

| Component | Technology |
|---|---|
| LLM | Groq `llama-3.3-70b-versatile` |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector Store | FAISS (`faiss-cpu`) — dual index |
| Web Search | Tavily API |
| LLM Framework | LangChain (`langchain-groq`) |
| PDF Parsing | PyMuPDF (`fitz`) |
| UI | Streamlit |
| Deployment | Streamlit Cloud |

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/AHZ002/ComplyRAG.git
cd ComplyRAG/AI_UseCase
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up API keys

Create a `.env` file in the `AI_UseCase/` directory:
```
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

Get your keys from:
- **Groq:** [https://console.groq.com/keys](https://console.groq.com/keys) (free)
- **Tavily:** [https://app.tavily.com](https://app.tavily.com) (free tier: 1000 searches/month)

### 5. Run the app
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 💬 Example Queries

| Query | Route Used |
|---|---|
| What are the core functions of the NIST Cybersecurity Framework? | 📄 Local RAG |
| What is the NIST framework's Identify function? | 📄 Local RAG |
| What are the ISO 27001 Annex A controls? | 🌐 Web Search |
| What are the SOC 2 trust service criteria? | 🌐 Web Search |
| Is our password policy compliant with NIST? | 🔍 Gap Analysis |
| What are the gaps in our incident response policy? | 🔍 Gap Analysis |
| Does our company policy address NIST core functions? | 🔍 Gap Analysis |

---

## ✨ Features

### Mandatory (Assignment Requirements)
- ✅ **RAG Integration** — FAISS vector index over NIST CSF PDF, top-3 chunk retrieval per query
- ✅ **Live Web Search** — Tavily API triggered automatically when local similarity score < 0.55
- ✅ **Response Modes** — Toggle between Concise (2-3 sentences) and Detailed (structured explanation) in sidebar

### Additional Enhancements
- ✅ **Company Policy Gap Analysis** — Dual FAISS index compares company security policy against compliance frameworks, identifying compliant areas, gaps, and recommendations
- ✅ **Intelligent Query Routing** — Keyword detection routes compliance queries to gap analysis, framework queries to RAG or web search
- ✅ **Source Attribution** — Every response shows whether it came from local documents, gap analysis, or web search
- ✅ **Web Source Links** — Expandable section shows source URLs from Tavily results
- ✅ **Chat History** — Full conversation history with last 3 turns passed to LLM for context
- ✅ **Anti-Hallucination Prompts** — Separate system prompts for Q&A and gap analysis both explicitly forbid fabricating compliance requirements
- ✅ **Singleton Embedding Model** — Loaded once via `@st.cache_resource`, not on every query
- ✅ **Clean Error Handling** — All functions wrapped in `try/except` with descriptive messages

---

## 🔧 Configuration

All settings are in `config/config.py`:
```python
GROQ_MODEL = "llama-3.3-70b-versatile"
SIMILARITY_THRESHOLD = 0.55   # Score below this triggers web search
TOP_K = 3                     # Number of document chunks to retrieve
DATA_DIR = "data/"            # Framework documents directory
COMPANY_DATA_DIR = "data/company/"  # Company policy documents directory
```

---

## ☁️ Deployment (Streamlit Cloud)

1. Push your code to a public GitHub repository
2. Go to [https://share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path** to `AI_UseCase/app.py`
5. Under **Advanced settings → Secrets**, add:
```toml
GROQ_API_KEY = "your_groq_api_key"
TAVILY_API_KEY = "your_tavily_api_key"
```

6. Click Deploy

---

## 🔮 Future Enhancements

- **Hybrid retrieval** — Combine FAISS semantic search with BM25 keyword matching for more precise compliance term retrieval
- **Compliance scoring** — Generate a quantitative compliance score with detailed breakdown by framework control

---

*Built by Abdul Hadi Zeeshan — March 2026*
