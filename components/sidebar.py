import streamlit as st
from utils.memory_manager import get_all_chats, create_chat, get_messages

def render_sidebar():
    """
    Renders the modern sidebar dynamically with production data.
    """
    with st.sidebar:
        # Brand & Workspace
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 32px; padding: 8px 0;">
                <div style="background-color: var(--primary-color); width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>
                </div>
                <div>
                    <h2 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: var(--primary-color); letter-spacing: -0.01em; padding: 0; border: none; margin-top: 0;">API Docs</h2>
                    <span style="font-size: 0.8rem; color: #B59B9B; font-weight: 400;">Documentation Assistant</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # New Chat Button
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            st.session_state.current_chat_id = create_chat()
            st.session_state.chat_history = []
            st.session_state.active_sources = []
            st.rerun()
        
        # Spacer
        st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

        # CHAT HISTORY
        st.markdown("<div style='font-size: 13px; font-weight: 600; color: var(--primary-color); margin-bottom: 12px;'>Recent Chats</div>", unsafe_allow_html=True)
        all_chats = get_all_chats()
        recent_chats = all_chats[:5] if all_chats else []
        
        if not recent_chats:
            st.markdown("<div style='font-size: 0.9rem; color: var(--text-muted); padding: 0.5rem 0;'>No conversations yet.</div>", unsafe_allow_html=True)
        else:
            for chat in recent_chats:
                title = chat["title"]
                display_title = title if len(title) <= 35 else title[:35] + "..."
                if st.button(f"💭 {display_title}", key=f"chat_{chat['id']}", use_container_width=True):
                    st.session_state.current_chat_id = chat["id"]
                    # Restore messages
                    msgs = get_messages(chat["id"])
                    st.session_state.chat_history = []
                    for m in msgs:
                        if m["role"] == "user":
                            st.session_state.chat_history.append({"role": "user", "question": m["content"]})
                        else:
                            st.session_state.chat_history.append({"role": "assistant", "answer": m["content"], "sources": m.get("sources", [])})
                    st.rerun()

        # COLLECTIONS
        st.markdown("<div style='font-size: 13px; font-weight: 600; color: var(--primary-color); margin-top: 32px; margin-bottom: 12px;'>Collections</div>", unsafe_allow_html=True)
        
        # Group chats by category
        collections = {}
        collection_order = []
        if all_chats:
            for chat in all_chats:
                cat = chat.get("category", "General")
                if cat == "General":
                    continue
                if cat not in collections:
                    collections[cat] = []
                    collection_order.append(cat)
                collections[cat].append(chat)
                
        # Limit to top 2 collections
        top_collections = collection_order[:2]
                
        if not top_collections:
            st.markdown("<div style='font-size: 0.9rem; color: var(--text-disabled); padding: 0.5rem 0;'>No collections yet.</div>", unsafe_allow_html=True)
        else:
            for col_name in top_collections:
                chats = collections[col_name][:2]  # Limit to 2 files/chats per collection
                with st.expander(f"📁 {col_name}"):
                    for chat in chats:
                        title = chat["title"]
                        display_title = title if len(title) <= 35 else title[:35] + "..."
                        if st.button(f"💭 {display_title}", key=f"col_chat_{chat['id']}", use_container_width=True):
                            st.session_state.current_chat_id = chat["id"]
                            msgs = get_messages(chat["id"])
                            st.session_state.chat_history = []
                            for m in msgs:
                                if m["role"] == "user":
                                    st.session_state.chat_history.append({"role": "user", "question": m["content"]})
                                else:
                                    st.session_state.chat_history.append({"role": "assistant", "answer": m["content"], "sources": m.get("sources", [])})
                            st.rerun()

        # Bottom Navigation (Settings)
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        
        if "show_settings" not in st.session_state:
            st.session_state.show_settings = False
            
        if st.button("⚙️ Settings", use_container_width=True, key="settings_btn"):
            st.session_state.show_settings = not st.session_state.show_settings
            
        if st.session_state.show_settings:
            with st.container():
                st.markdown("<div style='padding: 10px; background-color: var(--bg-card); border-radius: 8px; border: 1px solid var(--border-color); margin-top: 8px;'>", unsafe_allow_html=True)
                st.markdown("**Configuration**")
                st.selectbox("LLM Provider", ["OpenAI (GPT-4o)", "Anthropic (Claude 3.5)", "Local (Llama 3)"], index=0, key="mock_provider")
                st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1, key="mock_temp")
                st.number_input("Context Window (Tokens)", min_value=1000, max_value=128000, value=8000, step=1000, key="mock_ctx")
                st.toggle("Enable Web Search", value=False, key="mock_web")
                st.markdown("</div>", unsafe_allow_html=True)
