import streamlit as st
import os
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from models.llm import get_chatgroq_model, get_chat_response
from models.embeddings import load_embedding_model
from utils.rag import load_documents, build_faiss_index, retrieve_relevant_chunks, is_relevant
from utils.search import web_search

# ── System prompt for compliance assistant ──────────────────────────────────
SYSTEM_PROMPT = """You are ComplyRAG, an expert AI compliance assistant specialized in 
information security and compliance frameworks including NIST Cybersecurity Framework, 
ISO 27001, and SOC 2. 

You help organizations understand compliance requirements, security controls, 
and best practices. You provide accurate, reliable information based on official 
documentation and trusted sources.

Do NOT make up or assume any compliance requirements, controls, or standards.
If you are unsure, clearly say so and direct the user to official documentation."""


@st.cache_resource(show_spinner="Loading compliance documents...")
def initialize_rag():
    """Initialize RAG pipeline — runs once and caches"""
    try:
        model = load_embedding_model()
        chunks = load_documents()
        index = build_faiss_index(chunks, model)
        return model, chunks, index
    except Exception as e:
        st.error(f"Failed to initialize RAG: {str(e)}")
        return None, None, None


def instructions_page():
    """Instructions and setup page"""
    st.title("📋 ComplyRAG — Compliance Assistant")
    st.markdown("Welcome! Follow these instructions to set up and use the chatbot.")

    st.markdown("""
    ## 🔧 Installation

    First, install the required dependencies:
```bash
    pip install -r requirements.txt
```

    ## 🔑 API Key Setup

    You'll need the following API keys:

    ### Groq
    - Visit [Groq Console](https://console.groq.com/keys)
    - Create a new API key
    - Set `GROQ_API_KEY` in your `.env` file

    ### Tavily
    - Visit [Tavily](https://app.tavily.com)
    - Create a new API key
    - Set `TAVILY_API_KEY` in your `.env` file

    ## 📝 How It Works

    1. **RAG Pipeline** — Queries are first searched against local compliance documents
    2. **Web Search Fallback** — If local documents don't have relevant information, 
       Tavily web search is triggered automatically
    3. **Response Modes** — Switch between Concise and Detailed responses in the sidebar

    ## 💬 Example Questions

    - What are the core functions of the NIST Cybersecurity Framework?
    - What are ISO 27001 Annex A controls?
    - How does SOC 2 differ from ISO 27001?
    - What is the NIST framework's identify function?
    - What are the SOC 2 trust service criteria?

    ## ⚠️ Troubleshooting

    - **API Key Issues**: Make sure your `.env` file contains valid API keys
    - **Slow startup**: First load downloads the embedding model (~30 seconds)
    - **No results**: Try rephrasing your question

    ---

    Ready to start? Navigate to the **Chat** page using the sidebar!
    """)


def chat_page():
    """Main chat interface page"""
    st.title("🛡️ ComplyRAG — AI Compliance Assistant")
    st.caption("Powered by NIST CSF documentation + Live web search for ISO 27001 & SOC 2")

    # ── Sidebar settings ────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        response_mode = st.radio(
            "Response Mode",
            ["Concise", "Detailed"],
            index=0,
            help="Concise: 2-3 sentence replies. Detailed: In-depth explanations."
        )
        st.divider()
        st.markdown("### 📚 Knowledge Sources")
        st.success("✅ NIST CSF Document (Local RAG)")
        st.info("🌐 Web Search")
        st.divider()
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # ── Initialize RAG ───────────────────────────────────────────────────────
    embedding_model, chunks, faiss_index = initialize_rag()

    if embedding_model is None:
        st.error("Failed to load compliance documents. Please check your setup.")
        return

    # ── Initialize chat model ────────────────────────────────────────────────
    try:
        chat_model = get_chatgroq_model()
    except Exception as e:
        st.error(f"Failed to initialize chat model: {str(e)}")
        return

    # ── Initialize chat history ──────────────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ── Display chat history ─────────────────────────────────────────────────
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ── Chat input ───────────────────────────────────────────────────────────
    if prompt := st.chat_input("Ask about NIST, ISO 27001, SOC 2, or any compliance topic..."):

        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching compliance knowledge base..."):

                # ── Step 1: RAG retrieval ────────────────────────────────────
                context, score = retrieve_relevant_chunks(
                    prompt, faiss_index, chunks, embedding_model
                )

                # ── Step 2: Decide RAG vs Web Search ─────────────────────────
                if is_relevant(score):
                    source_type = "rag"
                    source_label = f"📄 Source: Local NIST CSF Document (similarity: {score:.2f})"
                else:
                    with st.spinner("Searching the web for latest compliance information..."):
                        context, urls = web_search(prompt)
                        source_type = "web"
                        source_label = "🌐 Source: Live Web Search"

                # ── Step 3: Generate response ────────────────────────────────
                response = get_chat_response(
                    chat_model,
                    st.session_state.messages,
                    SYSTEM_PROMPT,
                    context,
                    response_mode
                )

                # ── Step 4: Display response ─────────────────────────────────
                st.markdown(response)
                st.caption(source_label)

                # Show web sources if applicable
                if source_type == "web" and 'urls' in locals() and urls:
                    with st.expander("🔗 Web Sources"):
                        for url in urls:
                            st.markdown(f"- {url}")

        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response})


def main():
    st.set_page_config(
        page_title="ComplyRAG — AI Compliance Assistant",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    chat_page()


if __name__ == "__main__":
    main()