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
                st.markdown('<div class="settings-container-hook"></div>', unsafe_allow_html=True)
                st.markdown("<h3 style='font-size: 20px; font-weight: 600; color: var(--primary-color); margin-bottom: 20px; margin-top: 0;'>Configuration</h3>", unsafe_allow_html=True)
                
                st.markdown("""
                <style>
                    /* Custom Scrollbar for Sidebar */
                    [data-testid="stSidebarUserContent"]::-webkit-scrollbar {
                        width: 6px !important;
                        background-color: transparent !important;
                    }
                    [data-testid="stSidebarUserContent"]::-webkit-scrollbar-track {
                        background: #F9FAFB !important;
                        border-radius: 10px !important;
                    }
                    [data-testid="stSidebarUserContent"]::-webkit-scrollbar-thumb {
                        background: var(--primary-color) !important;
                        border-radius: 10px !important;
                    }

                    /* Settings Container Card */
                    div[data-testid="stVerticalBlock"]:has(.settings-container-hook) {
                        background-color: #FFFFFF !important;
                        border-radius: 18px !important;
                        border: 1px solid var(--border-color) !important;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.04) !important;
                        padding: 24px !important;
                        margin-top: 16px !important;
                        gap: 16px !important;
                    }

                    /* General Input Styling inside settings */
                    div[data-testid="stVerticalBlock"]:has(.settings-container-hook) label {
                        font-size: 16px !important;
                        font-weight: 500 !important;
                        color: var(--text-primary) !important;
                        padding-bottom: 8px !important;
                    }
                    div[data-testid="stVerticalBlock"]:has(.settings-container-hook) .stSelectbox div[data-baseweb="select"] {
                        height: 48px !important;
                        border-radius: 12px !important;
                        border-color: var(--border-color) !important;
                        background-color: #FFFFFF !important;
                    }
                    div[data-testid="stVerticalBlock"]:has(.settings-container-hook) .stSelectbox div[data-baseweb="select"]:hover {
                        border-color: var(--primary-color) !important;
                    }
                    
                    /* Number Input (Context Window) */
                    div[data-testid="stVerticalBlock"]:has(.settings-container-hook) .stNumberInput button {
                        width: 40px !important;
                        height: 40px !important;
                        border-radius: 8px !important;
                        background-color: #F3F4F6 !important;
                        border: none !important;
                        transition: all 0.2s ease !important;
                    }
                    div[data-testid="stVerticalBlock"]:has(.settings-container-hook) .stNumberInput button:hover {
                        background-color: #E5E7EB !important;
                    }
                    div[data-testid="stVerticalBlock"]:has(.settings-container-hook) .stNumberInput input {
                        text-align: center !important;
                        font-size: 15px !important;
                    }

                    /* Slider (Temperature) */
                    div[data-testid="stVerticalBlock"]:has(.settings-container-hook) .stSlider [role="slider"] {
                        width: 20px !important;
                        height: 20px !important;
                        background-color: var(--primary-color) !important;
                        box-shadow: 0 2px 6px rgba(109, 18, 43, 0.3) !important;
                        border: 2px solid #FFFFFF !important;
                        transition: transform 0.1s ease !important;
                    }
                    div[data-testid="stVerticalBlock"]:has(.settings-container-hook) .stSlider [role="slider"]:hover {
                        transform: scale(1.15) !important;
                    }
                    div[data-testid="stVerticalBlock"]:has(.settings-container-hook) div[data-baseweb="slider"] > div {
                        height: 4px !important;
                    }
                    div[data-testid="stVerticalBlock"]:has(.settings-container-hook) div[data-baseweb="slider"] > div > div:first-child {
                        background-color: var(--primary-color) !important;
                    }
                    div[data-testid="stVerticalBlock"]:has(.settings-container-hook) div[data-baseweb="slider"] > div > div:last-child {
                        background-color: #E5E7EB !important;
                    }

                    /* Toggle Switch */
                    div[data-testid="stVerticalBlock"]:has(.settings-container-hook) .stToggle [data-baseweb="checkbox"] > div {
                        background-color: #E5E7EB !important;
                    }
                    div[data-testid="stVerticalBlock"]:has(.settings-container-hook) .stToggle [data-baseweb="checkbox"] input:checked + div {
                        background-color: var(--primary-color) !important;
                    }

                    /* Settings Header Button */
                    [data-testid="stSidebar"] button:has(p:contains("⚙️ Settings")) {
                        height: 48px !important;
                        border: 1px solid var(--primary-color) !important;
                        background-color: #FFFFFF !important;
                        border-radius: 12px !important;
                    }
                    [data-testid="stSidebar"] button:has(p:contains("⚙️ Settings")) p {
                        font-weight: 600 !important;
                        color: var(--primary-color) !important;
                    }
                    [data-testid="stSidebar"] button:has(p:contains("⚙️ Settings")):hover {
                        background-color: #FCF0F2 !important;
                        transform: translateY(-1px) !important;
                    }
                </style>
                """, unsafe_allow_html=True)
                
                st.selectbox("LLM Provider", ["OpenAI (GPT-4o)", "Anthropic (Claude 3.5)", "Local (Llama 3)"], index=0, key="mock_provider")
                st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1, key="mock_temp")
                st.number_input("Context Window (Tokens)", min_value=1000, max_value=128000, value=8000, step=1000, key="mock_ctx")
                st.toggle("Enable Web Search", value=False, key="mock_web")
