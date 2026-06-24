import streamlit as st
from dotenv import load_dotenv

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI,
)

from langchain_community.vectorstores import Chroma

# =====================================
# Load Environment Variables
# =====================================
load_dotenv()

if "show_results" not in st.session_state:
    st.session_state.show_results = False

if "last_question" not in st.session_state:
    st.session_state.last_question = ""

if "active_response" not in st.session_state:
    st.session_state.active_response = None

if "active_sources" not in st.session_state:
    st.session_state.active_sources = []


@st.cache_resource
def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )


@st.cache_resource
def get_vector_store(_embeddings: GoogleGenerativeAIEmbeddings) -> Chroma:
    return Chroma(
        persist_directory="./chroma_db",
        embedding_function=_embeddings,
    )


@st.cache_resource
def get_retriever(_vector_store: Chroma):
    return _vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 2},
    )


@st.cache_resource
def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
    )


@st.cache_resource(show_spinner=False)
def get_embeddings():
    """Create the Gemini embeddings model once per Streamlit session."""
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )


@st.cache_resource(show_spinner=False)
def get_vector_store():
    """Load the persisted ChromaDB store once and reuse it across reruns."""
    return Chroma(
        persist_directory="./chroma_db",
        embedding_function=get_embeddings(),
    )


@st.cache_resource(show_spinner=False)
def get_retriever():
    """Build the retriever once so Streamlit reruns do not rebuild it."""
    return get_vector_store().as_retriever(
        search_type="similarity",
        search_kwargs={"k": 2},
    )

# =====================================
# Page Configuration
# =====================================
st.set_page_config(
    page_title="API Documentation Assistant",
    page_icon="A",
    layout="wide",
)

if "show_results" not in st.session_state:
    st.session_state.show_results = False

if "answer_content" not in st.session_state:
    st.session_state.answer_content = ""

if "source_chunks" not in st.session_state:
    st.session_state.source_chunks = []

if "search_query" not in st.session_state:
    st.session_state.search_query = ""


def reset_search_state():
    """Return the UI to the landing state without reloading the app."""
    st.session_state.show_results = False
    st.session_state.answer_content = ""
    st.session_state.source_chunks = []
    st.session_state.search_query = ""

# =====================================
# Custom CSS
# =====================================
st.markdown(
    """
    <style>
    :root {
        --app-bg: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
        --surface: rgba(255, 255, 255, 0.78);
        --surface-strong: rgba(255, 255, 255, 0.92);
        --border: rgba(15, 23, 42, 0.10);
        --border-strong: rgba(15, 23, 42, 0.14);
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --accent: #2563eb;
        --accent-soft: rgba(37, 99, 235, 0.10);
        --shadow-lg: 0 24px 80px rgba(15, 23, 42, 0.10);
        --shadow-md: 0 12px 32px rgba(15, 23, 42, 0.08);
        --radius-xl: 24px;
        --radius-lg: 18px;
        --radius-md: 14px;
    }

    [data-testid="stAppViewContainer"] {
        background: var(--app-bg);
    }

    [data-testid="stAppViewContainer"] > .main {
        padding-top: 1.25rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.96) 0%, rgba(30, 41, 59, 0.98) 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    [data-testid="stSidebar"] * {
        color: rgba(255, 255, 255, 0.92);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stSidebar"] label {
        color: rgba(255, 255, 255, 0.82) !important;
    }

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 1.25rem;
        padding: 0.9rem 1rem;
        background: rgba(255, 255, 255, 0.68);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        backdrop-filter: blur(18px);
        box-shadow: var(--shadow-md);
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        min-width: 0;
    }

    .brand-mark {
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 14px;
        background: linear-gradient(135deg, #0f172a 0%, #2563eb 100%);
        box-shadow: 0 16px 40px rgba(37, 99, 235, 0.32);
        flex: 0 0 auto;
    }

    .brand-copy {
        display: flex;
        flex-direction: column;
        min-width: 0;
    }

    .brand-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.1;
        margin: 0;
    }

    .brand-subtitle {
        font-size: 0.85rem;
        color: var(--text-secondary);
        line-height: 1.3;
        margin: 0.2rem 0 0;
    }

    .nav-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: flex-end;
    }

    .nav-pill {
        padding: 0.5rem 0.85rem;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: rgba(255, 255, 255, 0.75);
        color: var(--text-secondary);
        font-size: 0.85rem;
        font-weight: 600;
        white-space: nowrap;
    }

    .hero {
        padding: 1.5rem 0 1.25rem;
    }

    .hero-kicker {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.75rem;
        border-radius: 999px;
        background: rgba(37, 99, 235, 0.10);
        color: #1d4ed8;
        border: 1px solid rgba(37, 99, 235, 0.14);
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        margin-bottom: 0.9rem;
    }

    .hero-title {
        font-size: clamp(2.1rem, 3.4vw, 4rem);
        line-height: 1.02;
        letter-spacing: -0.04em;
        font-weight: 800;
        color: var(--text-primary);
        margin: 0 0 0.85rem;
        max-width: 14ch;
    }

    .hero-copy {
        color: var(--text-secondary);
        font-size: 1.02rem;
        line-height: 1.7;
        max-width: 62rem;
        margin: 0 0 1.2rem;
    }

    .surface-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        backdrop-filter: blur(18px);
        box-shadow: var(--shadow-lg);
    }

    .search-card {
        padding: 0.85rem 0.95rem 0.95rem;
        margin-bottom: 0.6rem;
    }

    .search-label {
        font-size: 0.82rem;
        font-weight: 750;
        color: var(--text-primary);
        margin-bottom: 0.45rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .search-hint {
        margin: 0.35rem 0 0.1rem;
        color: var(--text-secondary);
        font-size: 0.88rem;
    }

    .answer-card,
    .source-card,
    .empty-card {
        background: var(--surface-strong);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-md);
    }

    .answer-card {
        padding: 1.25rem 1.25rem 1rem;
    }

    .answer-title,
    .section-title {
        font-size: 1.05rem;
        font-weight: 750;
        color: var(--text-primary);
        margin: 0 0 0.85rem;
        letter-spacing: -0.01em;
    }

    .answer-content {
        color: var(--text-primary);
        font-size: 1rem;
        line-height: 1.75;
        white-space: normal;
        word-break: break-word;
    }

    .source-card {
        padding: 1rem 1rem 0.9rem;
        margin-bottom: 0.85rem;
    }

    .source-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        margin-bottom: 0.7rem;
    }

    .source-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.3rem 0.65rem;
        border-radius: 999px;
        background: var(--accent-soft);
        color: #1d4ed8;
        font-size: 0.8rem;
        font-weight: 700;
    }

    .source-body {
        max-height: 300px;
        overflow: auto;
        border-radius: var(--radius-md);
        border: 1px solid rgba(15, 23, 42, 0.08);
        background: #fafafa;
        padding: 0.9rem;
    }

    .source-body pre {
        margin: 0;
        white-space: pre-wrap;
        word-break: break-word;
        font-size: 0.92rem;
        line-height: 1.6;
        color: #0f172a;
    }

    .empty-grid {
        display: grid;
        grid-template-columns: repeat(12, minmax(0, 1fr));
        gap: 1rem;
    }

    .empty-hero {
        grid-column: span 8;
        padding: 1.4rem;
    }

    .empty-panel {
        grid-column: span 4;
        padding: 1.4rem;
    }

    .info-card {
        padding: 1rem 1rem 1.05rem;
        border-radius: 18px;
        border: 1px solid rgba(37, 99, 235, 0.16);
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.94) 0%, rgba(30, 41, 59, 0.96) 100%);
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.18);
        color: rgba(255, 255, 255, 0.94);
    }

    .info-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2rem;
        height: 2rem;
        border-radius: 999px;
        background: rgba(59, 130, 246, 0.18);
        border: 1px solid rgba(96, 165, 250, 0.28);
        color: #bfdbfe;
        margin-bottom: 0.7rem;
        font-size: 1rem;
    }

    .info-title {
        font-size: 0.95rem;
        font-weight: 800;
        color: rgba(255, 255, 255, 0.98);
        margin-bottom: 0.35rem;
        letter-spacing: -0.01em;
    }

    .info-copy {
        font-size: 0.92rem;
        line-height: 1.6;
        color: rgba(226, 232, 240, 0.9);
        margin: 0;
    }

    .empty-title {
        font-size: 1.2rem;
        font-weight: 750;
        color: var(--text-primary);
        margin-bottom: 0.6rem;
    }

    .empty-copy {
        color: var(--text-secondary);
        line-height: 1.7;
        margin-bottom: 0.95rem;
    }

    .example-list {
        display: grid;
        gap: 0.65rem;
    }

    .example-item {
        padding: 0.8rem 0.9rem;
        border-radius: 16px;
        border: 1px solid var(--border);
        background: rgba(248, 250, 252, 0.88);
        color: var(--text-primary);
        line-height: 1.5;
    }

    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.75rem;
        margin-top: 1rem;
    }

    .metric-card {
        padding: 0.95rem;
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.10);
        background: rgba(255, 255, 255, 0.06);
    }

    .metric-label {
        font-size: 0.78rem;
        color: rgba(255, 255, 255, 0.65);
        margin-bottom: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .metric-value {
        font-size: 1rem;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.96);
    }

    .sidebar-section {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.10);
    }

    .sidebar-title {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: rgba(255, 255, 255, 0.52);
        margin-bottom: 0.8rem;
    }

    .sidebar-item {
        padding: 0.8rem 0.9rem;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 0.65rem;
    }

    .sidebar-item strong {
        display: block;
        color: rgba(255, 255, 255, 0.95);
        margin-bottom: 0.15rem;
    }

    .sidebar-item span {
        color: rgba(255, 255, 255, 0.72);
        font-size: 0.9rem;
        line-height: 1.4;
    }

    .stButton > button {
        width: 100%;
        min-height: 3.15rem;
        border: 0;
        border-radius: 16px;
        padding: 0 1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0f172a 0%, #2563eb 100%);
        color: white;
        box-shadow: 0 16px 34px rgba(37, 99, 235, 0.28);
        margin-top: 0;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 20px 40px rgba(37, 99, 235, 0.32);
    }

    .stTextInput input {
        min-height: 3.15rem;
        border-radius: 16px;
        border: 1px solid var(--border-strong);
        background: rgba(255, 255, 255, 0.95);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
    }

    .stTextInput > div {
        margin-bottom: 0;
    }

    [data-testid="stHorizontalBlock"] {
        align-items: end;
        gap: 0.6rem;
    }

    [data-testid="stHorizontalBlock"] [data-testid="column"] {
        align-self: end;
    }

    [data-testid="stHorizontalBlock"] [data-testid="column"]:has(.stButton) {
        display: flex;
        align-items: end;
    }

    [data-testid="stHorizontalBlock"] [data-testid="column"]:has(.stButton) .stButton {
        width: 100%;
    }

    [data-testid="stHorizontalBlock"] [data-testid="column"]:has(.stTextInput) {
        display: flex;
        align-items: end;
    }

    [data-testid="stForm"] {
        margin-top: 0;
        margin-bottom: 0;
    }

    [data-testid="stFormSubmitButton"] button {
        min-height: 3.15rem;
    }

    .back-button-wrap {
        margin: 0 0 0.9rem;
        display: flex;
        justify-content: flex-start;
    }

    .back-button-wrap .stButton > button {
        width: auto;
        min-height: 2.75rem;
        padding: 0 1rem;
        background: rgba(255, 255, 255, 0.88);
        color: var(--text-primary);
        border: 1px solid var(--border-strong);
        box-shadow: var(--shadow-md);
    }

    .back-button-wrap .stButton > button:hover {
        background: rgba(255, 255, 255, 0.98);
        box-shadow: var(--shadow-lg);
    }

    .results-fade {
        animation: resultsFade 220ms ease-out;
    }

    @keyframes resultsFade {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stTextInput input:focus {
        border-color: rgba(37, 99, 235, 0.6);
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
    }

    @media (max-width: 1100px) {
        .empty-hero,
        .empty-panel {
            grid-column: span 12;
        }

        .metrics-grid {
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 768px) {
        [data-testid="stAppViewContainer"] > .main {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .topbar {
            flex-direction: column;
            align-items: flex-start;
        }

        .nav-pills {
            justify-content: flex-start;
        }

        .hero-title {
            max-width: 100%;
        }

        [data-testid="stHorizontalBlock"] {
            gap: 0.6rem;
        }

        [data-testid="stHorizontalBlock"] [data-testid="column"]:has(.stButton) {
            align-items: stretch;
        }

        [data-testid="stHorizontalBlock"] [data-testid="column"]:has(.stTextInput) {
            align-items: stretch;
        }

        .search-card {
            padding: 0.8rem 0.85rem 0.85rem;
        }

        .back-button-wrap {
            justify-content: stretch;
        }

        .back-button-wrap .stButton > button {
            width: 100%;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# =====================================
# Sidebar
# =====================================
with st.sidebar:
    st.markdown(
        """
        <div class="brand-copy" style="margin-top: 0.25rem; margin-bottom: 1rem;">
            <p class="brand-title" style="color: rgba(255,255,255,0.98);">API Documentation Assistant</p>
            <p class="brand-subtitle" style="color: rgba(255,255,255,0.68);">Premium RAG workspace for documentation search</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-section">
            <div class="sidebar-title">Workspace</div>
            <div class="sidebar-item">
                <strong>Search Mode</strong>
                <span>Semantic retrieval over indexed API documentation</span>
            </div>
            <div class="sidebar-item">
                <strong>Response Style</strong>
                <span>Grounded answers with retrieved source context</span>
            </div>
            <div class="sidebar-item">
                <strong>Experience</strong>
                <span>Fast, clean, and responsive AI assistant interface</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-section">
            <div class="sidebar-title">System Status</div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Model</div>
                    <div class="metric-value">Gemini 2.5 Flash</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Vector DB</div>
                    <div class="metric-value">ChromaDB</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Retriever</div>
                    <div class="metric-value">Top 2</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-section">
            <div class="sidebar-title">Tips</div>
            <div class="sidebar-item">
                <strong>Best results</strong>
                <span>Ask precise questions about authentication, keys, permissions, or errors.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =====================================
# Header
# =====================================

st.markdown(
    """
    <div class="topbar">
        <div class="brand">
            <div class="brand-mark"></div>
            <div class="brand-copy">
                <p class="brand-title">API Documentation Assistant</p>
                <p class="brand-subtitle">Enterprise-grade documentation search with grounded AI answers</p>
            </div>
        </div>
        <div class="nav-pills">
            <div class="nav-pill">Search</div>
            <div class="nav-pill">Sources</div>
            <div class="nav-pill">Grounded Answers</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
        <div class="hero-kicker">RAG-powered documentation experience</div>
        <h1 class="hero-title">Find answers across your API docs in seconds.</h1>
        <p class="hero-copy">
            Ask natural language questions and get concise, documented answers backed by the sources you already trust.
            The interface is designed like a modern SaaS product: clean, responsive, and built for clarity.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

# =====================================
# Load ChromaDB
# =====================================
embeddings = get_embeddings()

vector_store = get_vector_store(embeddings)

# =====================================
# Better Retriever
# =====================================
retriever = get_retriever(vector_store)

# =====================================
# Gemini
# =====================================
llm = get_llm()

# =====================================
# Search Section
# =====================================

st.markdown(
    """
    <div class="surface-card search-card">
        <div class="search-label">Search documentation</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("search_form", clear_on_submit=False):
    search_col, button_col = st.columns([6, 1])

    with search_col:
        question = st.text_input(
            "",
            placeholder="Ask a question about your API...",
            label_visibility="collapsed",
            value=st.session_state.last_question,
        )

    with button_col:
        search_button = st.form_submit_button(
            "Search",
            use_container_width=True,
        )

st.markdown(
    "<div class='search-hint'>Try questions about authentication flows, API key handling, permissions, or error responses.</div>",
    unsafe_allow_html=True,
)

search_triggered = search_button and bool(question)

if search_triggered:
    st.session_state.last_question = question
    st.session_state.show_results = True
    st.session_state.active_response = None
    st.session_state.active_sources = []

# =====================================
# Empty State
# =====================================
if not st.session_state.show_results:
    st.markdown(
        """
        <div class="empty-card">
            <div class="empty-grid">
                <div class="empty-hero">
                    <div class="empty-title">Start with a question</div>
                    <div class="empty-copy">
                        This workspace searches your documentation and returns grounded answers from the retrieved context.
                        Enter a question above to begin.
                    </div>
                    <div class="example-list">
                        <div class="example-item">How do I authenticate with the API?</div>
                        <div class="example-item">How do I generate an API key and how long does it last?</div>
                        <div class="example-item">What does a 401 Unauthorized error mean?</div>
                        <div class="example-item">How should I use the API key in a request header?</div>
                    </div>
                </div>
                <div class="empty-panel">
                    <div class="empty-title">What you can expect</div>
                    <div class="empty-copy">
                        Premium answer cards, clean source previews, and a responsive interface that works across desktop,
                        tablet, and mobile.
                    </div>
                    <div class="info-card" role="note" aria-label="Grounded answers information card">
                        <div class="info-icon" aria-hidden="true">?</div>
                        <div class="info-title">Grounded answers</div>
                        <p class="info-copy">Responses are generated only from the retrieved documentation.</p>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.session_state.show_results and not st.session_state.active_response and question:
    with st.spinner("Searching documentation..."):
        docs = retriever.invoke(question)

        context = "\n\n".join(
            [doc.page_content for doc in docs]
        )

        prompt = f"""
You are an API documentation assistant.

Use ONLY the provided documentation.

If the answer is not found in the documentation,
reply exactly:

I don't have enough information to answer that.

Documentation:
{context}

Question:
{question}
"""

        response = llm.invoke(prompt)

        unique_chunks = []

        for doc in docs:
            if doc.page_content not in unique_chunks:
                unique_chunks.append(
                    doc.page_content
                )

        st.session_state.active_response = response.content
        st.session_state.active_sources = unique_chunks

# =====================================
# Ask
# =====================================
if st.session_state.show_results and st.session_state.active_response:

    st.markdown('<div class="results-fade">', unsafe_allow_html=True)

    back_col, _ = st.columns([1, 7])

    with back_col:
        if st.button("Back to Search", use_container_width=True):
            st.session_state.show_results = False
            st.session_state.active_response = None
            st.session_state.active_sources = []
            st.session_state.last_question = ""
            st.rerun()

    # ==========================
    # Answer
    # ==========================
    st.markdown("<div class='section-title'>Answer</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="answer-card">
            <div class="answer-content">{st.session_state.active_response}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ==========================
    # Sources
    # ==========================
    st.markdown("<div class='section-title' style='margin-top: 1.25rem;'>Sources</div>", unsafe_allow_html=True)

    with st.expander(
        "Retrieved Documentation",
        expanded=False,
    ):
        for i, chunk in enumerate(st.session_state.active_sources):
            st.markdown(
                f"""
                <div class="source-card">
                    <div class="source-meta">
                        <div class="source-badge">Source {i + 1}</div>
                    </div>
                    <div class="source-body">
                        <pre>{chunk}</pre>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

st.caption(
    "LangChain • Gemini • ChromaDB • Streamlit"
)
