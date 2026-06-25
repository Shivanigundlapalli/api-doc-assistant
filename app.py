import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

from utils.logger import get_logger
from config import is_debug_mode, show_admin_panel, get_google_api_key, get_openai_api_key, get_langsmith_key
from utils.startup import validate_environment

# Run validation before importing other heavy local modules
validate_environment()

logger = get_logger("app")

# Map Streamlit Secrets to os.environ for Cloud Deployment (e.g. for LangSmith)
secret_keys = [
    "OPENAI_API_KEY", "GOOGLE_API_KEY", 
    "LANGCHAIN_API_KEY", "LANGCHAIN_PROJECT", "LANGCHAIN_TRACING_V2"
]
try:
    for key in secret_keys:
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])
except Exception:
    pass

from services.evaluation_service import initialize_langsmith
initialize_langsmith()

# Import core services
from services.vector_store_service import initialize_vector_store, build_vector_store, get_retriever
from services.llm_service import generate_answer, check_guardrails, rewrite_query
from utils.document_loaders import load_documents
from utils.text_processing import split_documents, deduplicate_docs

# Import UI components
from components.styling import inject_custom_css
from components.sidebar import render_sidebar
from components.hero import render_hero
from components.chat_interface import render_source_chip

# ==========================
# Page Configuration
# ==========================
st.set_page_config(
    page_title="API Documentation Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom CSS for SaaS look
inject_custom_css()

# ==========================
# Initialization & State
# ==========================
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "rebuild_db" not in st.session_state:
    st.session_state.rebuild_db = False
if "retrieval_cache" not in st.session_state:
    st.session_state.retrieval_cache = {}
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None
if "active_sources" not in st.session_state:
    st.session_state.active_sources = []

# Handle Vector DB Initialization
docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
init_logs = []

try:
    get_google_api_key()
    gemini_loaded = True
except Exception as e:
    gemini_loaded = False
    logger.error(f"Failed to load Gemini key: {e}")

openai_loaded = bool(get_openai_api_key())
langsmith_loaded = bool(get_langsmith_key())

is_cloud = (
    "STREAMLIT_RUNTIME_ENV" in os.environ or 
    os.environ.get("USER") == "appuser" or
    "mount/src" in __file__ or
    "streamlit" in os.environ.get("HOSTNAME", "").lower()
)
env_name = "Streamlit Cloud" if is_cloud else "Local"

try:
    if not gemini_loaded:
        st.error("Missing required configuration. Please add your API keys in Streamlit Secrets.")
        st.stop()
        
    with st.spinner("Preparing documentation index..." if not is_debug_mode() else "Initializing Vector Database..."):
        # Check if docs directory exists
        if not os.path.exists(docs_dir):
            logger.error(f"Documentation directory missing at {docs_dir}")
            st.error("Critical Error: Documentation directory missing.")
            st.stop()
            
        docs_files = [f for f in os.listdir(docs_dir) if os.path.isfile(os.path.join(docs_dir, f))]
        total_docs = len(docs_files)
        
        if total_docs == 0:
            logger.error("No documentation files found in 'docs/' directory.")
            st.error("Critical Error: No documentation files found.")
            st.stop()
            
        if st.session_state.rebuild_db:
            init_logs.append("Force rebuilding database...")
            logger.info("Force rebuilding vector database.")
            docs = load_documents(docs_dir)
            chunks = split_documents(docs)
            vector_store = build_vector_store(chunks)
            st.session_state.rebuild_db = False
            st.rerun()
        else:
            vector_store = initialize_vector_store()
            if vector_store is None:
                init_logs.append("Database missing or empty. Rebuilding...")
                logger.info("Database missing or empty. Rebuilding vector store...")
                docs = load_documents(docs_dir)
                chunks = split_documents(docs)
                vector_store = build_vector_store(chunks)
            else:
                init_logs.append("Successfully loaded existing vector database.")
                logger.info("Successfully loaded existing vector database.")

        retriever = get_retriever(vector_store) if vector_store else None
        total_chunks = vector_store._collection.count() if vector_store else 0
        
        init_logs.append(f"Loaded documents: {total_docs}")
        init_logs.append(f"Vector count: {total_chunks}")
        init_logs.append("Retriever initialized successfully.")
        logger.info(f"Retriever initialized. Docs: {total_docs}, Vectors: {total_chunks}")

except Exception as e:
    logger.error(f"Global exception during initialization: {e}\n{traceback.format_exc()}")
    st.error("Something went wrong. Please try again.")
    st.stop()

# Admin Dashboard
from components.admin import render_admin_dashboard
render_admin_dashboard(total_docs, total_chunks, gemini_loaded, openai_loaded, langsmith_loaded, env_name)

# Startup Diagnostics Panel (Collapsible - Only if DEBUG is True)
if is_debug_mode():
    with st.expander("🛠️ Startup Diagnostics & Telemetry (DEBUG MODE)", expanded=True):
        st.write(f"**Running Environment:** {env_name}")
        st.write(f"**Gemini Key Loaded:** {gemini_loaded}")
        st.write(f"**OpenAI Key Loaded:** {openai_loaded}")
        st.write(f"**LangSmith Key Loaded:** {langsmith_loaded}")
        for log in init_logs:
            st.text(log)

# ==========================
# UI Layout
# ==========================
# Left Sidebar (approx 18% dictated by CSS width 320px)
render_sidebar()

# Split into Center (Main Chat - 55%) and Right (Context Panel - 25%)
# Assuming sidebar is ~20%. So out of remaining 80%, we want 55 and 25.
# 55 / 80 = 68.75%, 25 / 80 = 31.25%
col_main, col_ctx = st.columns([68, 32], gap="large")

with col_ctx:
    st.markdown("""
        <div class="context-panel">
            <div class="context-header">Sources</div>
    """, unsafe_allow_html=True)
    
    if docs_files:
        for file in docs_files:
            st.markdown(f"""
                <div class="context-item">
                    <span class="context-icon">📄</span> {file}
                </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No documents uploaded.")
        
    st.divider()
    
    st.markdown("<div class='context-header'>Code Examples</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class="context-item"><span class="context-icon">🐍</span> Python</div>
        <div class="context-item"><span class="context-icon">🟨</span> JavaScript</div>
        <div class="context-item"><span class="context-icon">⚡</span> cURL</div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("<div class='context-header'>Related Questions</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class="context-item">How do I generate an API key?</div>
        <div class="context-item">Why am I getting 401?</div>
        <div class="context-item">What are the rate limits?</div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("<div class='context-header'>Document Sections</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class="context-item">Authentication</div>
        <div class="context-item">Rate Limits</div>
        <div class="context-item">Error Codes</div>
    """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

with col_main:
    if not st.session_state.chat_history:
        render_hero()

    # Chat History
    for i, msg in enumerate(st.session_state.get("chat_history", [])):
        with st.chat_message("user"):
            st.markdown(msg["question"])
        with st.chat_message("assistant", avatar="🤖"):
            from utils.parser import parse_enterprise_answer
            from components.chat_interface import render_enterprise_answer
            
            parsed = parse_enterprise_answer(msg["answer"])
            active_sources = render_enterprise_answer(parsed, msg.get("sources", []), msg_index=i)
            if active_sources:
                st.session_state.active_sources = active_sources

    if st.session_state.pending_query:
        query = st.session_state.pending_query
        st.session_state.pending_query = None
    else:
        query = st.chat_input("Ask anything about your API documentation...")

    if query:
        # 1. Render User Message
        with st.chat_message("user"):
            st.markdown(query)
        
        # 2. Guardrails Check
        with st.spinner("Analyzing query..."):
            try:
                if not check_guardrails(query):
                    err_msg = "I can answer only questions related to the uploaded documentation."
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(err_msg)
                    if "chat_history" not in st.session_state:
                        st.session_state.chat_history = []
                    st.session_state.chat_history.append({"question": query, "answer": err_msg, "sources": []})
                    st.stop()
            except Exception as e:
                st.error(f"Error checking guardrails: {e}")
                st.stop()
                
        # 3. Query Rewriting
        with st.spinner("Optimizing search..."):
            try:
                optimized_query = rewrite_query(query)
                if optimized_query != query:
                    st.caption(f"Optimized search: *{optimized_query}*")
            except Exception as e:
                optimized_query = query
                
        # 4. Retrieval & Answer Generation
        with st.spinner("Searching documentation..."):
            try:
                if not retriever:
                    st.error("Vector database is not initialized. Please add documents.")
                    st.stop()
                    
                if optimized_query in st.session_state.retrieval_cache:
                    raw_docs = st.session_state.retrieval_cache[optimized_query]
                else:
                    raw_docs = retriever.invoke(optimized_query)
                    st.session_state.retrieval_cache[optimized_query] = raw_docs
                    
                docs = deduplicate_docs(raw_docs)
                context = "\n\n".join([doc.page_content for doc in docs])
                
                answer_stream = generate_answer(optimized_query, context, memory=st.session_state.get("chat_history", []))
                
                # 5. Stream Response into Native UI
                with st.chat_message("assistant", avatar="🤖"):
                    st.caption("✨ Generating structural response...")
                    answer = st.write_stream(answer_stream)
                    
                    # After stream completes, we do not need to manually render the action buttons here
                    # because st.rerun() will immediately trigger the history loop which parses and renders the beautiful components.
                    
                    if is_debug_mode():
                        with st.expander("🔍 Query Telemetry (Admin)", expanded=False):
                            st.caption(f"Retrieved {len(docs)} document chunks.")
                            for i, doc in enumerate(docs):
                                st.caption(f"**Chunk {i+1} Metadata:** {doc.metadata}")
                
                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = []
                    
                st.session_state.chat_history.append({
                    "question": query, 
                    "answer": answer,
                    "sources": docs
                })
                
                st.rerun()
            except Exception as e:
                st.error(f"Error during retrieval or answer generation: {e}")
