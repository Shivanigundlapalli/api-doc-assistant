import streamlit as st
import os
import time
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
from services.vector_store.chroma_manager import initialize_vector_store, build_vector_store
from services.retriever.retriever_manager import get_retriever
from services.error_handler.handler import PipelineError
from services.startup.health_check import run_health_checks

docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
init_logs = []
startup_report = {}
health_status = "System Degraded"

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
    with st.spinner("Initializing Production System..."):
        docs_files = []
        if os.path.exists(docs_dir):
            docs_files = [f for f in os.listdir(docs_dir) if os.path.isfile(os.path.join(docs_dir, f))]
        
        vector_store = None
        retriever = None
        total_docs = len(docs_files)
        total_chunks = 0
        
        # 1. Initialize Vector Store
        if "vector_store" not in st.session_state or st.session_state.vector_store is None:
            v_store, needs_rebuild = initialize_vector_store(docs_dir)
            
            if needs_rebuild or st.session_state.get("rebuild_db", False):
                if total_docs == 0:
                    raise PipelineError("Startup", "No documentation files found in 'docs/' directory.")
                logger.info("Rebuilding vector store...")
                docs = load_documents(docs_dir)
                chunks = split_documents(docs)
                v_store = build_vector_store(chunks, docs_dir)
                st.session_state.rebuild_db = False
                total_chunks = len(chunks)
            else:
                logger.info("Successfully loaded existing vector database.")
                if v_store:
                    try:
                        total_chunks = v_store._collection.count()
                    except Exception:
                        total_chunks = 0
            
            st.session_state.vector_store = v_store
            
            # 2. Initialize Retriever
            if v_store:
                st.session_state.retriever = get_retriever(v_store)
                
        vector_store = st.session_state.vector_store
        retriever = st.session_state.get("retriever")
            
        # 3. Health Checks
        startup_report, health_status = run_health_checks(vector_store, retriever, total_docs)
        
        if "Failed" in startup_report.values():
            st.error("System startup failed. Check diagnostics panel.")
            st.stop()

except PipelineError as pe:
    logger.error(f"Pipeline Error during init: {pe}")
    st.error(f"Initialization Failed: {pe.reason}")
    st.stop()
except Exception as e:
    import traceback
    logger.error(f"Global exception during initialization: {e}\n{traceback.format_exc()}")
    st.error("Documentation indexing failed. Please contact an administrator.")
    st.stop()

# Admin Dashboard
from components.admin import render_admin_dashboard
render_admin_dashboard(total_docs, total_chunks, gemini_loaded, openai_loaded, langsmith_loaded, env_name)

# Startup Diagnostics Panel (Collapsible - Only if DEBUG is True)
from config import is_debug_mode
if is_debug_mode():
    with st.expander("🛠️ Startup Diagnostics & Telemetry (DEBUG MODE)", expanded=True):
        st.write(f"**Running Environment:** {env_name}")
        st.write(f"**Gemini Key Loaded:** {gemini_loaded}")
        st.write(f"**OpenAI Key Loaded:** {openai_loaded}")
        st.write(f"**LangSmith Key Loaded:** {langsmith_loaded}")
        
        st.markdown("### Startup Report")
        if startup_report and isinstance(startup_report, dict):
            for key, value in startup_report.items():
                st.write(f"**{key}:** {value}")
            
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

if not st.session_state.chat_history:
    render_hero()

# Chat History
from components.chat_interface import render_source_chips

for i, msg in enumerate(st.session_state.get("chat_history", [])):
    with st.chat_message(msg.get("role", "user")):
        st.markdown(msg.get("answer", msg.get("question", msg.get("content", ""))))
        if msg.get("role") == "assistant" and msg.get("sources"):
            render_source_chips(msg.get("sources"), confidence=msg.get("confidence", 0))

if st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None
else:
    st.markdown('<span id="chat-btn-anchor"></span>', unsafe_allow_html=True)

    query = st.chat_input("Ask anything about your API documentation...")

if query:
    # 1. Render User Message
    with st.chat_message("user"):
        st.markdown(query)
        
    add_message(st.session_state.current_chat_id, "user", query)
    
    # Check Cache First to prevent redundant API calls
    if "query_cache" not in st.session_state:
        st.session_state.query_cache = {}
        
    normalized_query = query.strip().lower()
    
    top_docs = []
    confidence = 0
    category = "General"
    answer_stream = None
    compressed_context = ""
    is_cached = False
    
    if normalized_query in st.session_state.query_cache:
        st.toast("Retrieved from Cache! ⚡", icon="⚡")
        cache_hit = st.session_state.query_cache[normalized_query]
        top_docs = cache_hit["top_docs"]
        confidence = cache_hit["confidence"]
        
        def cached_generator():
            yield cache_hit["answer"]
            
        answer_stream = cached_generator()
        is_cached = True
    else:
        # 2. Agent Execution via LangGraph
        from services.agent.graph import create_production_agent_graph
        import json
        
        agent_app = create_production_agent_graph()
        
        with st.status("Understanding question...", expanded=True) as status:
            state = {
                "question": query,
                "memory": st.session_state.get("chat_history", []),
                "retriever": retriever,
                "is_allowed": True,
                "optimized_query": "",
                "category": "",
                "raw_docs": [],
                "deduped_docs": [],
                "top_docs": [],
                "confidence": 0,
                "compressed_context": "",
                "error_message": "",
                "answer_stream": None
            }
            
            try:
                for output in agent_app.stream(state):
                    if not output: continue
                    
                    if isinstance(output, dict):
                        for key, value in output.items():
                            if key == "analyze_query":
                                status.update(label="Searching...", state="running")
                            elif key == "retrieve":
                                status.update(label="Retrieving...", state="running")
                            elif key == "rerank":
                                status.update(label="Ranking...", state="running")
                            elif key == "context_validation":
                                status.update(label="Generating...", state="running")
                            elif key == "llm":
                                pass # Stream starting
                            
                            if isinstance(value, dict):
                                if value.get("error_message"):
                                    status.update(label="Error", state="error")
                                    err_json = value.get("error_message")
                                    try:
                                        err_dict = json.loads(err_json)
                                        err_msg = err_dict.get("reason", "An error occurred.")
                                    except:
                                        err_msg = err_json
                                        
                                    with st.chat_message("assistant", avatar="🤖"):
                                        st.markdown(err_msg)
                                    st.session_state.chat_history.append({"role": "user", "question": query})
                                    st.session_state.chat_history.append({"role": "assistant", "answer": err_msg, "sources": []})
                                    from utils.memory_manager import add_message
                                    add_message(st.session_state.current_chat_id, "assistant", err_msg)
                                    st.stop()
                                    
                                if "top_docs" in value: top_docs = value.get("top_docs", [])
                                if "confidence" in value: confidence = value.get("confidence", 0)
                                if "category" in value: category = value.get("category", "")
                                
                                # Handle multiple possible answer fields
                                if "answer_stream" in value and value.get("answer_stream") is not None:
                                    answer_stream = value.get("answer_stream")
                                elif "answer" in value and value.get("answer") is not None:
                                    answer_stream = value.get("answer")
                                elif "response" in value and value.get("response") is not None:
                                    answer_stream = value.get("response")
                                elif "final_answer" in value and value.get("final_answer") is not None:
                                    answer_stream = value.get("final_answer")
                                    
                                if "compressed_context" in value: compressed_context = value.get("compressed_context", "")
            
                status.update(label="Done", state="complete", expanded=False)
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                from services.logging.logger import get_logger
                logger = get_logger("App.py")
                logger.error(f"Graph execution failed:\n{tb}")
                
                status.update(label="Error", state="error")
                err_msg = (
                    "We couldn't generate an answer right now.\n\n"
                    "Possible reasons:\n"
                    "• AI provider temporarily unavailable\n"
                    "• API quota exceeded\n"
                    "• Network issue\n\n"
                    "Please try again in a few moments."
                )
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(err_msg)
                st.session_state.chat_history.append({"role": "user", "question": query})
                st.session_state.chat_history.append({"role": "assistant", "answer": err_msg, "sources": []})
                
    if answer_stream is not None:
        # Stream Response into Native UI safely from the network generator
        with st.chat_message("assistant", avatar="🤖"):
            answer = ""
            try:
                
                if confidence >= 80:
                    st.markdown(f"<div style='display:inline-flex; align-items:center; background-color:var(--bg-secondary); padding:6px 14px; border-radius:20px; border:1px solid var(--border-color); font-size:13px; font-weight:500; color:var(--text-primary);'><span style='margin-right:8px; font-size:14px;'>🟢</span> High Confidence &nbsp;&middot;&nbsp; Grounded in {len(top_docs)} documentation sections</div>", unsafe_allow_html=True)
                elif confidence >= 40:
                    st.markdown(f"<div style='display:inline-flex; align-items:center; background-color:var(--bg-secondary); padding:6px 14px; border-radius:20px; border:1px solid var(--border-color); font-size:13px; font-weight:500; color:var(--text-primary);'><span style='margin-right:8px; font-size:14px;'>🟡</span> Medium Confidence &nbsp;&middot;&nbsp; Grounded in {len(top_docs)} documentation sections</div>", unsafe_allow_html=True)
                    
                start_time = time.time()
                
                # Check if we got a simple string vs a generator
                if isinstance(answer_stream, str):
                    st.markdown(answer_stream)
                    answer = answer_stream
                else:
                    answer = st.write_stream(answer_stream)
                    
                elapsed_time = time.time() - start_time
                from services.logging.logger import get_logger
                get_logger("App.py").info(f"Stream completed successfully. Length: {len(answer)}")
                
                # Save to cache if not already cached
                if not is_cached and answer:
                    st.session_state.query_cache[normalized_query] = {
                        "answer": answer,
                        "top_docs": top_docs,
                        "confidence": confidence
                    }
                    
                    # Keep cache small (LRU style, max 50)
                    if len(st.session_state.query_cache) > 50:
                        oldest_key = list(st.session_state.query_cache.keys())[0]
                        del st.session_state.query_cache[oldest_key]
                        
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                from services.logging.logger import get_logger
                get_logger("App.py").error(f"Streaming UI iteration failed:\n{tb}")
                if not answer:
                    answer = "The connection was interrupted while generating the response. Please try again."
                    st.error(answer)
                else:
                    st.warning("The connection was interrupted, but here is the partial response generated so far:")
                
            if answer and len(answer.strip()) < 30 and not "AI service disruption" in answer:
                err_str = f"The generated answer was too short ({len(answer)} chars): '{answer}'"
                from services.logging.logger import get_logger
                get_logger("App.py").error(err_str)
                if not top_docs:
                    st.error(err_str)
                
            if top_docs:
                render_source_chips(top_docs, confidence=confidence)
                
            # Add metadata footer
            st.markdown(
                f"<div style='font-size: 13px; color: var(--text-muted); margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border-color);'>"
                f"Generated in {elapsed_time:.1f} s &nbsp;•&nbsp; "
                f"Model: Gemini 2.5 Flash &nbsp;•&nbsp; "
                f"Retrieved {len(top_docs)} chunks &nbsp;•&nbsp; "
                f"Grounded in documentation</div>",
                unsafe_allow_html=True
            )
                
            st.session_state.chat_history.append({"role": "user", "question": query})
            st.session_state.chat_history.append({"role": "assistant", "answer": answer, "sources": top_docs, "confidence": confidence})
            
            source_dicts = [{"content": d.page_content, "metadata": d.metadata} for d in top_docs]
            from utils.memory_manager import add_message, update_chat_category
            add_message(st.session_state.current_chat_id, "assistant", answer, sources=source_dicts)
            update_chat_category(st.session_state.current_chat_id, category)
