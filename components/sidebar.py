import streamlit as st
from utils.memory_manager import get_all_chats, create_chat, get_messages

def render_sidebar():
    """
    Renders the modern sidebar dynamically with production data.
    """
    with st.sidebar:
        # Brand & Workspace
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 25px;">
                <div style="background-color: #C0392B; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 20px;">
                    <img src="https://example.com/avatar.png" width="30" height="30" style="border-radius:50%;" />
                </div>
                <div>
                    <h2 style="margin: 0; font-size: 1.2rem; font-weight: 600; color: #FFFFFF; letter-spacing: 0.5px;">API Docs</h2>
                    <span style="font-size: 0.75rem; color: #E7E1D8;">Documentation Assistant</span>
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
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

        # CHAT HISTORY
        st.markdown("<div class='sidebar-group-header'>Recent Chats</div>", unsafe_allow_html=True)
        all_chats = get_all_chats()
        recent_chats = all_chats[:5] if all_chats else []
        
        if not recent_chats:
            st.markdown("<div style='font-size: 0.85rem; color: rgba(255,255,255,0.5); padding: 0.5rem;'>No conversations yet.</div>", unsafe_allow_html=True)
        else:
            for chat in recent_chats:
                title = chat["title"]
                display_title = title if len(title) <= 35 else title[:35] + "..."
                if st.button(f"💬 {display_title}", key=f"chat_{chat['id']}", use_container_width=True):
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
        st.markdown("<div class='sidebar-group-header' style='margin-top: 25px;'>Collections</div>", unsafe_allow_html=True)
        
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
            st.markdown("<div style='font-size: 0.85rem; color: rgba(255,255,255,0.5); padding: 0.5rem;'>No collections yet.</div>", unsafe_allow_html=True)
        else:
            for col_name in top_collections:
                chats = collections[col_name][:2]  # Limit to 2 files/chats per collection
                with st.expander(f"📁 {col_name}"):
                    for chat in chats:
                        title = chat["title"]
                        display_title = title if len(title) <= 35 else title[:35] + "..."
                        if st.button(f"💬 {display_title}", key=f"col_chat_{chat['id']}", use_container_width=True):
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
            <div class='sidebar-bottom-nav'>
                <div class='sidebar-item'><span class='sidebar-item-icon'>⚙️</span> Settings</div>
                <div class='sidebar-item'><span class='sidebar-item-icon'>❓</span> Help & Support</div>
                <div class='sidebar-item' style='color: #FCA5A5 !important;'><span class='sidebar-item-icon'>🚪</span> Logout</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Appearance Toggle
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        st.toggle("Appearance (Dark Mode)", value=True)
