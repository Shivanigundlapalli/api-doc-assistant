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
    --bg-color: #0F172A;
    --card-bg: #111827;
    --secondary-bg: #1E293B;
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --border-color: #334155;
    
    --primary-color: #2563EB;
    --primary-hover: #3B82F6;
    --sidebar-grad-start: #0F172A;
    --sidebar-grad-end: #1E293B;
    
    --success-color: #10B981;
    --warning-color: #F59E0B;
    --danger-color: #EF4444;
    
    --shadow-card: 0 4px 20px rgba(0,0,0,0.2);
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
    max-width: 900px !important;
    margin: 0 auto;
}

/* Hide Default Streamlit Elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

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
    background-color: #0F172A !important;
    border-radius: 8px; /* Slightly smaller radius for inner code blocks */
    margin: 1rem 0;
    border: 1px solid var(--border-color);
}
.stCodeBlock code {
    color: #F8FAFC !important;
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
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 0.4rem 0.8rem;
    font-size: 0.85rem;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all var(--anim-speed) ease;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    margin-right: 0.5rem;
}
.btn-action:hover {
    background-color: var(--secondary-bg);
    color: var(--text-primary);
    border-color: var(--text-secondary);
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
    background: linear-gradient(145deg, rgba(37, 99, 235, 0.1), rgba(17, 24, 39, 1));
    border: 1px solid var(--primary-color);
    border-radius: var(--border-radius-base);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 0 15px rgba(37, 99, 235, 0.15);
}
.qa-title {
    color: var(--primary-color);
    font-weight: 700;
    margin-bottom: 0.5rem;
    font-size: 1.1rem;
}

</style>
    """, unsafe_allow_html=True)
