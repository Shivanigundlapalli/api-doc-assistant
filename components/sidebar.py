import streamlit as st

def render_sidebar():
    """
    Renders the modern sidebar dynamically with production data.
    """
    with st.sidebar:
        # Brand & Workspace
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 25px;">
                <div style="background-color: #E53E3E; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 20px;">
                    A
                </div>
                <div>
                    <h2 style="margin: 0; font-size: 1.2rem; font-weight: 600; color: #FFFFFF; letter-spacing: 0.5px;">API Docs</h2>
                    <span style="font-size: 0.75rem; color: #FCA5A5;">Documentation Assistant</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # New Chat Button
        st.button("➕ New Chat", use_container_width=True)
        
        # Spacer
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

        # CHAT HISTORY
        st.markdown("<div class='sidebar-group-header'>Recent Chats</div>", unsafe_allow_html=True)
        chat_history = st.session_state.get("chat_history", [])
        
        if not chat_history:
            st.markdown("<div style='font-size: 0.85rem; color: rgba(255,255,255,0.5); padding: 0.5rem;'>No conversations yet.</div>", unsafe_allow_html=True)
        else:
            for msg in chat_history:
                # Truncate question for sidebar display
                q = msg["question"]
                display_q = q if len(q) < 25 else q[:22] + "..."
                st.markdown(f"""
                    <div class='sidebar-item'>
                        <span class='sidebar-item-icon'>💬</span> {display_q}
                    </div>
                """, unsafe_allow_html=True)

        # COLLECTIONS
        st.markdown("<div class='sidebar-group-header' style='margin-top: 25px;'>Collections</div>", unsafe_allow_html=True)
        collections = st.session_state.get("collections", [])
        
        if not collections:
            st.markdown("<div style='font-size: 0.85rem; color: rgba(255,255,255,0.5); padding: 0.5rem;'>No collections available.</div>", unsafe_allow_html=True)
        else:
            for col in collections:
                st.markdown(f"""
                    <div class='sidebar-item'>
                        <span class='sidebar-item-icon'>📁</span> {col}
                    </div>
                """, unsafe_allow_html=True)

        # PINNED CHATS
        pinned_chats = st.session_state.get("pinned_chats", [])
        if pinned_chats:
            st.markdown("<div class='sidebar-group-header' style='margin-top: 25px;'>Pinned 📌</div>", unsafe_allow_html=True)
            for pin in pinned_chats:
                st.markdown(f"""
                    <div class='sidebar-item'>
                        <span class='sidebar-item-icon'>💬</span> {pin}
                    </div>
                """, unsafe_allow_html=True)

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
