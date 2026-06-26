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
from services.llm_service import generate_answer, check_guardrails
from utils.document_loaders import load_documents
from utils.text_processing import split_documents, deduplicate_docs

# Import UI components
from components.styling import inject_custom_css
from components.sidebar import render_sidebar
from components.hero import render_hero
from utils.memory_manager import create_chat, get_messages, add_message

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
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = create_chat()
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
if "pinned_chats" not in st.session_state:
    st.session_state.pinned_chats = []
if "collections" not in st.session_state:
    st.session_state.collections = []

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

# ==========================
# Main Chat Interface & Right Panel
# ==========================

st.markdown("<style>.stMainBlockContainer { max-width: 900px; padding-top: 2rem; }</style>", unsafe_allow_html=True)

if not st.session_state.chat_history:
    render_hero()

# Chat History
from components.chat_interface import render_source_chips

for i, msg in enumerate(st.session_state.get("chat_history", [])):
    with st.chat_message(msg.get("role", "user")):
        st.markdown(msg.get("answer", msg.get("question", msg.get("content", ""))))
        if msg.get("role") == "assistant" and msg.get("sources"):
            render_source_chips(msg.get("sources"))

if st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None
else:
    # Inject native floating buttons for Attach and Voice using CSS positioning
    st.markdown('<div class="floating-icons-anchor"></div>', unsafe_allow_html=True)
    
    # We will use CSS to position this block next to the send button
    st.markdown('<span id="chat-btn-anchor"></span>', unsafe_allow_html=True)
    col_empty, col1, col2 = st.columns([8, 1, 1])
    with col1:
        st.button("📎", key="attach_btn", help="Attach file")
    with col2:
        st.button("🎤", key="voice_btn", help="Voice input")

    query = st.chat_input("Ask anything about your API documentation...")

if query:
    # 1. Render User Message
    with st.chat_message("user"):
        st.markdown(query)
        
    add_message(st.session_state.current_chat_id, "user", query)
    
    # 2. Guardrails Check
    with st.spinner("Analyzing query..."):
        try:
            if not check_guardrails(query):
                err_msg = "I can answer only questions related to the uploaded documentation."
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(err_msg)
                st.session_state.chat_history.append({"role": "user", "question": query})
                st.session_state.chat_history.append({"role": "assistant", "answer": err_msg, "sources": []})
                add_message(st.session_state.current_chat_id, "assistant", err_msg)
                st.stop()
        except Exception as e:
            st.error(f"Error checking guardrails: {e}")
            st.stop()
            
    from services.llm_service import analyze_query, compress_context, rerank_and_score_confidence
    
    with st.status("Understanding your question...", expanded=True) as status:
        try:
            analysis = analyze_query(query, st.session_state.get("chat_history", []))
            optimized_query = analysis["rewritten_query"]
            category = analysis["category"]
            
            status.update(label="Optimizing search query...", state="running")
            
            if not retriever:
                status.update(label="Error: Vector database not initialized.", state="error")
                st.stop()
                
            status.update(label="Searching documentation...", state="running")
            if optimized_query in st.session_state.retrieval_cache:
                raw_docs = st.session_state.retrieval_cache[optimized_query]
            else:
                raw_docs = retriever.invoke(optimized_query)
                st.session_state.retrieval_cache[optimized_query] = raw_docs
                
            docs = deduplicate_docs(raw_docs)
            
            status.update(label="Ranking relevant sections...", state="running")
            rerank_result = rerank_and_score_confidence(optimized_query, docs, top_k=3)
            top_docs = rerank_result["top_chunks"]
            confidence = rerank_result["confidence"]
            
            if confidence < 85:
                status.update(label="Low confidence. Aborting generation.", state="error")
                err_msg = "I couldn't find this information in the uploaded documentation. You may want to upload the relevant API guide. I don't want to guess because that could produce inaccurate technical guidance."
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(err_msg)
                st.session_state.chat_history.append({"role": "user", "question": query})
                st.session_state.chat_history.append({"role": "assistant", "answer": err_msg, "sources": []})
                from utils.memory_manager import add_message
                add_message(st.session_state.current_chat_id, "assistant", err_msg)
                st.stop()
            
            status.update(label="Generating answer...", state="running")
            compressed_context = compress_context(optimized_query, top_docs)
            
            status.update(label="Response generated", state="complete", expanded=False)
            
        except Exception as e:
            status.update(label=f"Error: {e}", state="error")
            st.stop()

    # Step 8-11: Agent Reasoning & Streaming
    answer_stream = generate_answer(optimized_query, compressed_context, memory=st.session_state.get("chat_history", []), retriever=retriever)
    
    # Stream Response into Native UI
    with st.chat_message("assistant", avatar="🤖"):
        answer = st.write_stream(answer_stream)
        
        if top_docs:
            render_source_chips(top_docs)
            
        # Confidence Badge
        st.markdown(f"<div style='margin-top: 15px; font-size: 0.85rem; color: #16A34A; background-color: #DCFCE7; display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 12px; font-weight: 500;'>🛡️ Verified by Documentation | {confidence}% Confidence | {len(top_docs)} chunks used</div>", unsafe_allow_html=True)
        
        if is_debug_mode():
            with st.expander("🔍 Query Telemetry (Admin)", expanded=False):
                st.caption(f"**Intent Category:** {category}")
                st.caption(f"**Compressed Context Length:** {len(compressed_context)} chars")
                for i, doc in enumerate(top_docs):
                    st.caption(f"**Chunk {i+1} Metadata:** {doc.metadata}")
            
        st.session_state.chat_history.append({"role": "user", "question": query})
        st.session_state.chat_history.append({"role": "assistant", "answer": answer, "sources": top_docs})
        
        source_dicts = [{"content": d.page_content, "metadata": d.metadata} for d in top_docs]
        from utils.memory_manager import add_message, update_chat_category
        add_message(st.session_state.current_chat_id, "assistant", answer, sources=source_dicts)
        update_chat_category(st.session_state.current_chat_id, category)
        
        st.rerun()
