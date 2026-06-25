import streamlit as st

def render_sidebar():
    """
    Renders the modern sidebar (Professional Redesign Edition).
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
        
        # Search
        st.text_input("Search chats, docs...", placeholder="Search chats, docs... ⌘K", label_visibility="collapsed")
        
        # New Chat Button
        st.button("➕ New Chat", use_container_width=True)
        
        # Spacer
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

        # CHAT HISTORY
        st.markdown("<div class='sidebar-group-header'>CHAT HISTORY</div>", unsafe_allow_html=True)
        
        # Today
        st.markdown("<div style='font-size: 0.75rem; color: #FFFFFF; margin-top: 10px; margin-bottom: 4px;'>Today</div>", unsafe_allow_html=True)
        st.markdown("""
            <div class='sidebar-item'><span class='sidebar-item-icon'>💬</span> How do I authenticate? <span class='sidebar-item-right'>10:30 AM</span></div>
            <div class='sidebar-item'><span class='sidebar-item-icon'>💬</span> Rate limits overview <span class='sidebar-item-right'>09:15 AM</span></div>
            <div class='sidebar-item'><span class='sidebar-item-icon'>💬</span> Upload file API <span class='sidebar-item-right'>08:40 AM</span></div>
        """, unsafe_allow_html=True)
        
        # Yesterday
        st.markdown("<div style='font-size: 0.75rem; color: #FFFFFF; margin-top: 10px; margin-bottom: 4px;'>Yesterday</div>", unsafe_allow_html=True)
        st.markdown("""
            <div class='sidebar-item'><span class='sidebar-item-icon'>💬</span> 403 error meaning <span class='sidebar-item-right'>Yesterday</span></div>
            <div class='sidebar-item'><span class='sidebar-item-icon'>💬</span> Generate API key <span class='sidebar-item-right'>Yesterday</span></div>
        """, unsafe_allow_html=True)
        
        # Previous 7 Days
        st.markdown("<div style='font-size: 0.75rem; color: #FFFFFF; margin-top: 10px; margin-bottom: 4px;'>Previous 7 Days</div>", unsafe_allow_html=True)
        st.markdown("""
            <div class='sidebar-item'><span class='sidebar-item-icon'>💬</span> Pagination in API <span class='sidebar-item-right'>3 days ago</span></div>
            <div class='sidebar-item'><span class='sidebar-item-icon'>💬</span> Webhook configuration <span class='sidebar-item-right'>5 days ago</span></div>
        """, unsafe_allow_html=True)
        
        # COLLECTIONS
        st.markdown("<div class='sidebar-group-header' style='margin-top: 25px;'>COLLECTIONS</div>", unsafe_allow_html=True)
        st.markdown("""
            <div class='sidebar-item'><span class='sidebar-item-icon'>📁</span> Authentication Docs <span class='sidebar-item-right'>12</span></div>
            <div class='sidebar-item'><span class='sidebar-item-icon'>📁</span> Rate Limit Docs <span class='sidebar-item-right'>8</span></div>
            <div class='sidebar-item'><span class='sidebar-item-icon'>📁</span> OpenAPI Spec <span class='sidebar-item-right'>4</span></div>
            <div class='sidebar-item'><span class='sidebar-item-icon'>📁</span> SDK Guides <span class='sidebar-item-right'>6</span></div>
        """, unsafe_allow_html=True)

        # PINNED
        st.markdown("<div class='sidebar-group-header' style='margin-top: 25px;'>PINNED 📌</div>", unsafe_allow_html=True)
        st.markdown("""
            <div class='sidebar-item'><span class='sidebar-item-icon'>💬</span> How do I authenticate? <span class='sidebar-item-right'>📌</span></div>
            <div class='sidebar-item'><span class='sidebar-item-icon'>💬</span> Rate limits overview <span class='sidebar-item-right'>📌</span></div>
        """, unsafe_allow_html=True)

        # Bottom Navigation & Profile
        st.markdown("""
            <div class='sidebar-bottom-nav'>
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px; cursor: pointer;">
                    <div style="background-color: rgba(255,255,255,0.2); width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                        A
                    </div>
                    <div>
                        <div style="font-size: 0.9rem; font-weight: 600; color: #FFFFFF;">Aditya</div>
                        <div style="font-size: 0.75rem; color: #FCA5A5;">aditya@example.com</div>
                    </div>
                </div>
                
                <div class='sidebar-item'><span class='sidebar-item-icon'>⚙️</span> Settings</div>
                <div class='sidebar-item'><span class='sidebar-item-icon'>❓</span> Help & Support</div>
                <div class='sidebar-item' style='color: #FCA5A5 !important;'><span class='sidebar-item-icon'>🚪</span> Logout</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Appearance Toggle natively
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        st.toggle("Appearance (Dark Mode)", value=True)
