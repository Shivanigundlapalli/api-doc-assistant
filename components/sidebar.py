import streamlit as st

def render_sidebar():
    """
    Renders the modern sidebar (Burgundy Edition).
    """
    with st.sidebar:
        # Logo + Workspace
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 25px;">
                <div style="background-color: rgba(255,255,255,0.15); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 18px; border: 1px solid rgba(255,255,255,0.2);">
                    A
                </div>
                <div>
                    <h2 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #FFFFFF; letter-spacing: 0.5px;">API Docs</h2>
                    <span style="font-size: 0.75rem; color: rgba(255,255,255,0.7);">Assistant</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # New Chat Button
        st.markdown("""
            <div style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; padding: 10px; color: white; display: flex; align-items: center; gap: 8px; cursor: pointer; margin-bottom: 30px; font-weight: 500; font-size: 0.9rem;" onclick="window.location.reload();">
                <span>➕</span> New Chat
            </div>
        """, unsafe_allow_html=True)
        
        # Recent Chats
        st.markdown("<div style='font-size: 0.75rem; font-weight: 600; color: rgba(255,255,255,0.5); text-transform: uppercase; margin-bottom: 12px; letter-spacing: 0.05em;'>Recent Chats</div>", unsafe_allow_html=True)
        recent_chats = [
            "How do I authenticate?",
            "Rate limits",
            "Upload file",
            "403 error",
            "Generate API key"
        ]
        for chat in recent_chats:
            st.markdown(f"""
                <div style="color: rgba(255,255,255,0.85); font-size: 0.9rem; padding: 6px 0; cursor: pointer; display: flex; align-items: center; gap: 8px;">
                    <span style="opacity: 0.5; font-size: 12px;">💬</span> {chat}
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

        # Collections
        st.markdown("<div style='font-size: 0.75rem; font-weight: 600; color: rgba(255,255,255,0.5); text-transform: uppercase; margin-bottom: 12px; letter-spacing: 0.05em;'>Collections</div>", unsafe_allow_html=True)
        collections = [
            "Authentication Docs",
            "Rate Limit Docs",
            "OpenAPI Spec",
            "SDK Guides"
        ]
        for col in collections:
            st.markdown(f"""
                <div style="color: rgba(255,255,255,0.85); font-size: 0.9rem; padding: 6px 0; cursor: pointer; display: flex; align-items: center; gap: 8px;">
                    <span style="opacity: 0.5; font-size: 14px;">📁</span> {col}
                </div>
            """, unsafe_allow_html=True)

        # Spacer to push bottom navigation down
        st.markdown("<div style='flex-grow: 1; min-height: 150px;'></div>", unsafe_allow_html=True)
        
        # Bottom Navigation
        st.divider()
        st.markdown("""
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <div style="color: rgba(255,255,255,0.85); font-size: 0.9rem; cursor: pointer; display: flex; align-items: center; gap: 8px;">
                    <span>👤</span> Profile
                </div>
                <div style="color: rgba(255,255,255,0.85); font-size: 0.9rem; cursor: pointer; display: flex; align-items: center; gap: 8px;">
                    <span>⚙️</span> Settings
                </div>
                <div style="color: rgba(255,255,255,0.85); font-size: 0.9rem; cursor: pointer; display: flex; align-items: center; gap: 8px;">
                    <span>🌙</span> Dark Mode
                </div>
                <div style="color: rgba(255,255,255,0.85); font-size: 0.9rem; cursor: pointer; display: flex; align-items: center; gap: 8px;">
                    <span>🚪</span> Logout
                </div>
            </div>
        """, unsafe_allow_html=True)
