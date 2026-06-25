import streamlit as st
import os
from config import show_admin_panel

def render_admin_dashboard(total_docs, total_chunks, gemini_loaded, openai_loaded, langsmith_loaded, env_name):
    """
    Renders the secure Admin Dashboard if SHOW_ADMIN_PANEL=True.
    """
    if not show_admin_panel():
        return
        
    st.markdown("<div class='admin-header'>🛡️ Admin Dashboard</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Documents", total_docs)
    with col2:
        st.metric("Total Chunks", total_chunks)
    with col3:
        st.metric("Environment", env_name)
        
    st.divider()
    
    st.markdown("### 🔐 API Status")
    st.write(f"**Gemini Model:** {'🟢 Connected' if gemini_loaded else '🔴 Missing'}")
    st.write(f"**OpenAI Fallback:** {'🟢 Connected' if openai_loaded else '⚪ Not Configured'}")
    st.write(f"**LangSmith Tracing:** {'🟢 Connected' if langsmith_loaded else '⚪ Not Configured'}")
    
    st.divider()
    
    st.markdown("### 🗄️ Vector Database")
    db_path = os.path.abspath("chroma_db")
    st.caption(f"Path: `{db_path}`")
    st.write(f"Status: {'🟢 Online' if total_chunks > 0 else '🔴 Empty / Rebuilding'}")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
