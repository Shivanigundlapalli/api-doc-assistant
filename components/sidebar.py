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
        st.markdown("""
            <div style='margin-top: 40px; display: flex; flex-direction: column; gap: 8px;'>
                <div style='display: flex; align-items: center; gap: 8px; color: var(--text-primary); font-size: 14px; font-weight: 500; cursor: pointer; padding: 8px; border-radius: 8px; transition: background 0.2s;' onmouseover="this.style.background='#F0E6E6'" onmouseout="this.style.background='transparent'">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                    Settings
                </div>
            </div>
        """, unsafe_allow_html=True)
