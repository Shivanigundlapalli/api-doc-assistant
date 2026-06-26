import streamlit as st

def inject_custom_css():
    """
    Injects custom CSS to transform Streamlit into a modern enterprise SaaS application.
    Implements the Deep Burgundy Theme.
    """
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-color: #FAF8F4;
    --card-bg: #FFFFFF;
    --secondary-bg: #FEE2E2; /* Slightly softer for backgrounds if needed */
    --text-primary: #1F2937;
    --text-secondary: #6B7280;
    --border-color: #E7E1D8;
    
    --primary-color: #7A1F1F;
    --primary-hover: #A52A2A;
    --accent-color: #C0392B;
    --sidebar-grad-start: #7A1F1F;
    --sidebar-grad-end: #7A1F1F;
    
    --success-color: #16A34A;
    --warning-color: #D97706;
    --danger-color: #DC2626;
    
    --shadow-card: 0 4px 12px rgba(0,0,0,0.04);
    --border-radius-base: 16px;
    --anim-speed: 200ms;
}

/* Global Typography */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 400;
    color: var(--text-primary);
    background-color: var(--bg-color) !important;
}

h1, h2, h3, h4, h5, h6 {
    font-weight: 600 !important;
    color: var(--text-primary);
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Layout Overrides */
.stApp {
    background-color: var(--bg-color) !important;
}

/* Center Container max width to 900px */
.main .block-container {
    max-width: 1400px !important; /* The total width containing both Center and Right columns */
    padding-top: 2rem !important;
    padding-bottom: 5rem !important;
}

/* Center Column Specific Styling to keep text readable */
div[data-testid="column"]:nth-of-type(1) {
    max-width: 1400px !important;
    margin: 0 auto;
}

/* Hide Default Streamlit Elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header { background: transparent !important; }
header .stAppDeployButton { display: none !important; }

/* LEFT SIDEBAR (18%) */
/* Streamlit doesn't allow percentage width natively without risking broken layouts, 
   but we can force it with CSS. Default sidebar is around 320px, which is ~18% on a 1080p screen. */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--sidebar-grad-start) 0%, var(--sidebar-grad-end) 100%) !important;
    border-right: none !important;
    width: 320px !important;
}

/* Style all text inside Sidebar to be White */
section[data-testid="stSidebar"] * {
    color: rgba(255, 255, 255, 0.9) !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.1) !important;
}

/* Chat Messages */
.chat-message {
    padding: 1.5rem;
    border-radius: var(--border-radius-base);
    margin-bottom: 1.5rem;
    display: flex;
    gap: 1rem;
    font-size: 0.95rem;
    line-height: 1.6;
    transition: box-shadow var(--anim-speed) ease;
}

.chat-message.user {
    background-color: transparent;
}

.chat-message.assistant {
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-card);
}

.chat-avatar {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
}
.chat-message.user .chat-avatar {
    background-color: var(--secondary-bg);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}
.chat-message.assistant .chat-avatar {
    background-color: var(--primary-color);
    color: white;
}

/* Code Blocks */
.stCodeBlock {
    background-color: #F8FAFC !important;
    border-radius: 8px;
    margin: 1rem 0;
    border: 1px solid var(--border-color);
}
.stCodeBlock code {
    color: var(--text-primary) !important;
}

/* Search / Chat Input Sticky Bottom */
div[data-testid="stChatInput"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--border-radius-base) !important;
    box-shadow: var(--shadow-card) !important;
    transition: box-shadow var(--anim-speed) ease, border-color var(--anim-speed) ease;
}
div[data-testid="stChatInput"]:focus-within {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 2px rgba(139,30,45,0.2) !important;
}

/* Custom Buttons (Pills / Actions) */
.btn-action {
    background-color: #FFFFFF;
    border: 1px solid var(--primary-color);
    border-radius: 8px;
    padding: 0.4rem 0.8rem;
    font-size: 0.85rem;
    color: var(--primary-color);
    cursor: pointer;
    transition: all var(--anim-speed) ease;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    margin-right: 0.5rem;
}
.btn-action:hover {
    background-color: var(--primary-color);
    color: #FFFFFF;
    box-shadow: 0 0 10px rgba(139, 30, 30, 0.2);
}

/* Context Panel (Right Column) */
.context-panel {
    background-color: transparent;
    padding-left: 1rem;
    height: 100%;
}
.context-header {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
    margin-top: 1rem;
}
.context-item {
    font-size: 0.85rem;
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    transition: background var(--anim-speed) ease;
}
.context-item:hover {
    background-color: var(--secondary-bg);
    color: var(--text-primary);
}
.context-icon {
    color: var(--primary-color);
    font-size: 1rem;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}
.animated-fade {
    animation: fadeIn 0.3s ease-out;
}

/* Fix expanders */
div[data-testid="stExpander"] {
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    background: var(--card-bg) !important;
    margin-top: 1rem;
}

/* Quick Answer Card */
.quick-answer-card {
    background-color: var(--card-bg);
    border: 2px solid var(--primary-color);
    border-radius: var(--border-radius-base);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 15px rgba(139, 30, 30, 0.08);
}
.qa-title {
    color: var(--primary-color);
    font-weight: 700;
    margin-bottom: 0.5rem;
    font-size: 1.1rem;
}

/* =========================================
   UI SaaS Overrides
   ========================================= */

/* 1. Feedback Toast (Bottom Center) */
[data-testid="stToastContainer"] {
    top: auto !important;
    bottom: 2rem !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    right: auto !important;
    align-items: center !important;
    z-index: 9999 !important;
}

[data-testid="stToast"] {
    background-color: var(--card-bg) !important;
    border: 1px solid var(--primary-color) !important;
    border-radius: var(--border-radius-base) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    padding: 12px 20px !important;
}

[data-testid="stToast"] > div {
    color: var(--text-primary) !important;
    font-weight: 500 !important;
    text-align: center !important;
}

/* 2. Action Toolbar Buttons (Ghost style) */
.action-toolbar-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1rem;
}

div[data-testid="stHorizontalBlock"] > div.action-button-col {
    min-width: fit-content !important;
    flex: 0 1 auto !important;
}

div[data-testid="stHorizontalBlock"] > div.action-button-col button[data-testid="baseButton-secondary"] {
    height: 40px !important;
    border-radius: 12px !important;
    padding: 0 16px !important;
    border: none !important;
    background-color: transparent !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stHorizontalBlock"] > div.action-button-col button[data-testid="baseButton-secondary"]:hover {
    color: var(--primary-color) !important;
    background-color: rgba(139, 30, 45, 0.05) !important;
}

/* 3. Integrated Input Bar */
/* Move the Attach and Voice popovers into the chat input */
.integrated-input-container {
    position: relative;
    width: 100%;
}

.integrated-input-buttons {
    position: absolute;
    bottom: 6px;
    left: 10px;
    z-index: 999;
    display: flex;
    gap: 4px;
}

.integrated-input-buttons button[data-testid="baseButton-secondary"] {
    height: 36px !important;
    width: 36px !important;
    padding: 0 !important;
    border-radius: 8px !important;
    border: none !important;
    background: transparent !important;
    color: var(--text-secondary) !important;
    box-shadow: none !important;
    display: flex;
    align-items: center;
    justify-content: center;
}

.integrated-input-buttons button[data-testid="baseButton-secondary"]:hover {
    background-color: var(--secondary-bg) !important;
    color: var(--text-primary) !important;
}

/* Push text inside chat input to make room for absolute buttons */
div[data-testid="stChatInput"] textarea {
    padding-left: 90px !important;
}

/* =========================================
   Professional Sidebar Redesign
   ========================================= */

[data-testid="stSidebar"] {
    background-color: #7A1F1F !important;
    border-right: none !important;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* Sidebar Search Input */
[data-testid="stSidebar"] div[data-baseweb="input"] {
    background-color: rgba(0,0,0,0.15) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
}

[data-testid="stSidebar"] div[data-baseweb="input"]:focus-within {
    border: 1px solid #FCA5A5 !important;
}

[data-testid="stSidebar"] input {
    color: #FFFFFF !important;
}

/* Sidebar New Chat Button (Primary) */
[data-testid="stSidebar"] button[kind="primary"] {
    background-color: #891C1C !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

[data-testid="stSidebar"] button[kind="primary"]:hover {
    background-color: rgba(255,255,255,0.1) !important;
    border-color: #FCA5A5 !important;
}

[data-testid="stSidebar"] button[kind="primary"] p {
    color: #FFFFFF !important;
}

/* Sidebar Chat History Buttons (Secondary / White Boxes) */
[data-testid="stSidebar"] button[kind="secondary"] {
    background-color: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.1) !important;
    color: #C0392B !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    display: flex !important;
    justify-content: flex-start !important;
    align-items: center !important;
    padding: 0.5rem 1rem !important;
}

[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background-color: #F8FAFC !important;
    border-color: #C0392B !important;
}

/* Force text inside the white boxes to be red */
[data-testid="stSidebar"] button[kind="secondary"] p,
[data-testid="stSidebar"] button[kind="secondary"] span,
[data-testid="stSidebar"] button[kind="secondary"] div {
    color: #C0392B !important;
}

/* Sidebar Custom Links & Elements */
.sidebar-group-header {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: #E7E1D8 !important;
    text-transform: uppercase !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.5rem !important;
    letter-spacing: 0.05em !important;
}

.sidebar-item {
    font-size: 0.85rem !important;
    padding: 0.4rem 0.5rem !important;
    border-radius: 6px !important;
    color: rgba(255,255,255,0.85) !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    cursor: pointer !important;
    transition: background 0.2s ease !important;
    margin-bottom: 0.2rem !important;
}

.sidebar-item:hover {
    background-color: rgba(0,0,0,0.1) !important;
    color: #FFFFFF !important;
}

.sidebar-item-icon {
    font-size: 0.9rem !important;
    opacity: 0.8 !important;
}

.sidebar-item-right {
    margin-left: auto !important;
    font-size: 0.75rem !important;
    color: #FCA5A5 !important;
}

/* Bottom Nav Container */
.sidebar-bottom-nav {
    border-top: 1px solid rgba(255,255,255,0.1) !important;
    padding-top: 1rem !important;
    margin-top: 2rem !important;
}

/* =========================================
   Chat UI Overhaul (Mockup Match)
   ========================================= */

/* User Message Bubble */
[data-testid="stChatMessage"][data-baseweb="block"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background-color: #FAFAFA !important;
    border: 1px solid #FCA5A5 !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

/* Agent Message Bubble */
[data-testid="stChatMessage"][data-baseweb="block"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    background-color: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.05) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

/* Hide default avatars, we will custom style them or use native */
[data-testid="chatAvatarIcon-user"] {
    background-color: #E53E3E !important;
    color: white !important;
}

[data-testid="chatAvatarIcon-assistant"] {
    background-color: #891C1C !important;
    color: white !important;
}

/* Horizontal Action Buttons Wrapper */
.action-buttons-wrapper {
    display: flex !important;
    gap: 10px !important;
    margin-top: 15px !important;
    flex-wrap: wrap !important;
}

/* Action Button Styling */
.action-btn {
    border: 1px solid #FCA5A5 !important;
    color: #891C1C !important;
    background-color: transparent !important;
    border-radius: 8px !important;
    padding: 6px 14px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    transition: all 0.2s ease !important;
}

.action-btn:hover {
    background-color: rgba(229, 62, 62, 0.05) !important;
    border-color: #E53E3E !important;
}

/* Inline Sources Chips */
.source-chip {
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    border: 1px solid rgba(0,0,0,0.1) !important;
    border-radius: 8px !important;
    padding: 6px 12px !important;
    font-size: 0.8rem !important;
    color: #333 !important;
    background-color: #FFF !important;
    margin-right: 8px !important;
    margin-bottom: 8px !important;
    text-decoration: none !important;
}
.source-chip:hover {
    background-color: #F9F9F9 !important;
}

/* The native chat input container styling */
[data-testid="stChatInput"] {
    background-color: transparent !important;
}

[data-testid="stChatInput"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.1) !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05) !important;
    border-radius: 12px !important;
}

/* Send Button inside Input */
[data-testid="stChatInputSubmitButton"] {
    background-color: #891C1C !important;
    color: white !important;
    border-radius: 8px !important;
    width: 32px !important;
    height: 32px !important;
    margin-right: 8px !important;
}
[data-testid="stChatInputSubmitButton"] svg {
    fill: white !important;
}

/* Floating Native Action Buttons (Attach/Voice) */
/* Position them absolutely next to the chat input's send button */
div:has(> span#chat-btn-anchor) + div[data-testid="stHorizontalBlock"] {
    position: fixed !important;
    bottom: 3.5rem !important;
    right: 5.5rem !important;
    z-index: 99999 !important;
    width: auto !important;
    background: transparent !important;
}

div:has(> span#chat-btn-anchor) + div[data-testid="stHorizontalBlock"] > div {
    min-width: auto !important;
    width: auto !important;
    flex: 0 1 auto !important;
}

div:has(> span#chat-btn-anchor) + div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    border: 1px solid rgba(229, 62, 62, 0.3) !important;
    background-color: #FAFAFA !important;
    color: #891C1C !important;
    border-radius: 50% !important;
    width: 36px !important;
    height: 36px !important;
    padding: 0 !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    transition: all 0.2s ease !important;
}

div:has(> span#chat-btn-anchor) + div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
    border: 1px solid #E53E3E !important;
    background-color: rgba(229, 62, 62, 0.05) !important;
}

/* Ensure the chat input has enough padding on the right to not overlap text with our buttons */
[data-testid="stChatInput"] textarea {
    padding-right: 130px !important;
}
</style>
    """, unsafe_allow_html=True)
