import streamlit as st
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from models.llm import get_chatgroq_model, get_chat_response
from models.embeddings import load_embedding_model
from utils.rag import load_documents, build_faiss_index, retrieve_relevant_chunks, is_relevant
from utils.search import web_search
from utils.company_rag import load_company_documents, build_company_faiss_index, retrieve_company_chunks, is_compliance_query

# ── System prompts ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are ComplyRAG, an expert AI compliance assistant specialized in
information security and compliance frameworks including NIST Cybersecurity Framework,
ISO 27001, and SOC 2.

You help organizations understand compliance requirements, security controls,
and best practices. You provide accurate, reliable information based on official
documentation and trusted sources.

Do NOT make up or assume any compliance requirements, controls, or standards.
If you are unsure, clearly say so and direct the user to official documentation."""

GAP_ANALYSIS_PROMPT = """You are ComplyRAG, an expert AI compliance assistant performing 
a gap analysis between a company's security policy and compliance frameworks.

You will be given:
1. COMPANY POLICY CONTEXT: Relevant excerpts from the company's actual security policy
2. FRAMEWORK CONTEXT: Relevant excerpts from compliance frameworks (NIST, ISO 27001, SOC 2)

Your job is to:
- Compare the company policy against the framework requirements
- Clearly state what is COMPLIANT, what is MISSING, and what are the GAPS
- Be specific and reference actual policy text where possible
- Structure your response clearly with sections: Compliant Areas, Gaps Found, Recommendations

Do NOT fabricate policy content or framework requirements.
Only base your analysis on the context provided."""


@st.cache_resource(show_spinner="Loading compliance documents...")
def initialize_rag():
    """Initialize both RAG pipelines — runs once and caches"""
    try:
        model = load_embedding_model()

        # Framework index (existing)
        chunks = load_documents()
        index = build_faiss_index(chunks, model)

        # Company policy index (new)
        company_chunks = load_company_documents()
        company_index = build_company_faiss_index(company_chunks, model)

        return model, chunks, index, company_chunks, company_index
    except Exception as e:
        st.error(f"Failed to initialize RAG: {str(e)}")
        return None, None, None, None, None


def chat_page():
    """Main chat interface page"""
    st.title("🛡️ ComplyRAG — AI Compliance Assistant")
    st.caption("Powered by NIST CSF documentation + Company Policy Analysis + Live web search")

    # ── Sidebar settings ──────────────────────────────────────────────────────
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
        st.success("✅ TechCorp Security Policy (Gap Analysis)")
        st.info("🌐 Web Search (Any compliance topic)")
        st.divider()
        st.markdown("### 💡 Example Queries")
        st.caption("**Framework questions:**")
        st.caption("• What are NIST CSF core functions?")
        st.caption("• What is the Identify function?")
        st.caption("**Gap analysis questions:**")
        st.caption("• Is our password policy compliant with NIST?")
        st.caption("• What are the gaps in our incident response?")
        st.caption("• Does our company comply with NIST access control?")
        st.divider()
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # ── Initialize RAG ────────────────────────────────────────────────────────
    embedding_model, chunks, faiss_index, company_chunks, company_index = initialize_rag()

    if embedding_model is None:
        st.error("Failed to load compliance documents. Please check your setup.")
        return

    # ── Initialize chat model ─────────────────────────────────────────────────
    try:
        chat_model = get_chatgroq_model()
    except Exception as e:
        st.error(f"Failed to initialize chat model: {str(e)}")
        return

    # ── Initialize chat history ───────────────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ── Display chat history ──────────────────────────────────────────────────
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ── Chat input ────────────────────────────────────────────────────────────
    if prompt := st.chat_input("Ask about NIST, ISO 27001, SOC 2, or check your company policy compliance..."):

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            # ── Route 1: Gap Analysis ─────────────────────────────────────────
            if is_compliance_query(prompt):
                with st.spinner("Analyzing company policy against compliance frameworks..."):

                    # Retrieve from both indexes
                    company_context = retrieve_company_chunks(
                        prompt, company_index, company_chunks, embedding_model
                    )
                    framework_context, score = retrieve_relevant_chunks(
                        prompt, faiss_index, chunks, embedding_model
                    )

                    # If framework score is low, enrich with web search
                    if not is_relevant(score):
                        web_context, urls = web_search(prompt)
                        framework_context = web_context
                        source_label = "🔍 Source: Company Policy + Live Web Search (gap analysis)"
                    else:
                        urls = []
                        source_label = f"🔍 Source: Company Policy + NIST CSF Document (similarity: {score:.2f})"

                    # Build combined context
                    combined_context = f"""COMPANY POLICY CONTEXT:
{company_context}

FRAMEWORK CONTEXT:
{framework_context}"""

                    response = get_chat_response(
                        chat_model,
                        st.session_state.messages,
                        GAP_ANALYSIS_PROMPT,
                        combined_context,
                        response_mode
                    )

                    st.markdown(response)
                    st.caption(source_label)

                    if urls:
                        with st.expander("🔗 Web Sources"):
                            for url in urls:
                                st.markdown(f"- {url}")

            # ── Route 2: Normal RAG or Web Search (existing logic unchanged) ──
            else:
                with st.spinner("Searching compliance knowledge base..."):

                    context, score = retrieve_relevant_chunks(
                        prompt, faiss_index, chunks, embedding_model
                    )

                    if is_relevant(score):
                        source_label = f"📄 Source: Local NIST CSF Document (similarity: {score:.2f})"
                    else:
                        with st.spinner("Searching the web for latest compliance information..."):
                            context, urls = web_search(prompt)
                            source_label = "🌐 Source: Live Web Search"

                    response = get_chat_response(
                        chat_model,
                        st.session_state.messages,
                        SYSTEM_PROMPT,
                        context,
                        response_mode
                    )

                    st.markdown(response)
                    st.caption(source_label)

                    if source_label.startswith("🌐") and 'urls' in locals() and urls:
                        with st.expander("🔗 Web Sources"):
                            for url in urls:
                                st.markdown(f"- {url}")

        st.session_state.messages.append({"role": "assistant", "content": response})


def main():
    st.set_page_config(
        page_title="ComplyRAG — AI Compliance Assistant",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    with st.sidebar:
        st.title("🛡️ ComplyRAG")
        st.caption("AI Compliance Assistant")
        st.divider()

    chat_page()


if __name__ == "__main__":
    main()