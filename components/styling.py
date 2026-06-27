import streamlit as st

def inject_custom_css():
    """
    Injects custom CSS to transform Streamlit into a modern enterprise SaaS application.
    Implements a 10/10 production standard presentation comparable to Stripe/OpenAI Docs.
    """
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-color: #FAF8F5;
    --card-bg: #FFFFFF;
    --text-heading: #1E293B;
    --text-body: #475569;
    --border-color: #E7E7E7;
    
    --primary-color: #8B1E1E;
    --primary-hover: #A32626;
    
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --border-radius-base: 12px;
}

/* Global Typography & Spacing */
html, body, [class*="css"], .stMarkdown p, .stMarkdown li {
    font-family: 'Inter', sans-serif !important;
    font-weight: 400;
    color: var(--text-body);
    background-color: var(--bg-color) !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
}

/* Headings Base */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-heading) !important;
    letter-spacing: -0.01em !important;
}

h1 { font-size: 24px !important; margin-bottom: 24px !important; }
h2 { 
    font-size: 20px !important; 
    margin-top: 24px !important; 
    padding-top: 20px !important;
    margin-bottom: 16px !important; 
    border-top: 1px solid var(--border-color);
}
h3 { font-size: 16px !important; }

/* Remove top border from the very first h2 in a message */
.stChatMessage .stMarkdown > div > h2:first-of-type {
    border-top: none !important;
    padding-top: 0 !important;
    margin-top: 0 !important;
}

/* Section Icons using Pseudo-elements */
h2#direct-answer::before { content: '✓ '; color: var(--primary-color); }
h2#explanation::before { content: '📖 '; }
h2#steps::before { content: '🛠 '; }
h2#code-example::before, h2#example::before { content: '💻 '; }
h2#best-practices::before { content: '💡 '; }
h2#common-errors::before { content: '⚠️ '; }
h2#related-documentation::before { content: '🔗 '; }
h2#sources::before { content: '📄 '; }

/* Center Container max width to 900px */
.main .block-container {
    max-width: 900px !important;
    margin: 0 auto;
    padding-top: 2rem !important;
    padding-bottom: 5rem !important;
}

/* Hide Default Streamlit Elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header { background: transparent !important; }

/* Chat Messages */
.stChatMessage {
    background-color: var(--card-bg) !important;
    border-radius: 12px !important;
    padding: 24px !important;
    margin-bottom: 24px !important;
    border: 1px solid var(--border-color) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* User Message Bubble */
.stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 16px 0 !important;
    margin-bottom: 8px !important;
}

.stChatMessage[data-testid="stChatMessage"]:nth-child(odd) p {
    font-size: 24px !important; /* Question Title size */
    font-weight: 600 !important;
    color: var(--text-heading) !important;
}

/* NOTES / BEST PRACTICES - Subtle Info Card */
h2#best-practices + ul, h2#best-practices + p,
h2#common-errors + ul, h2#common-errors + p {
    background-color: #FAF8F5 !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 16px !important;
}

/* INLINE CODE */
code:not(pre code) {
    background-color: #F8FAFC !important;
    color: var(--text-heading) !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 15px !important;
    border: 1px solid #E2E8F0 !important;
}

/* CODE BLOCKS */
.stCodeBlock {
    background-color: #FAFAFA !important; /* Lighter theme as requested */
    border-radius: 8px !important;
    margin-top: 16px !important;
    margin-bottom: 24px !important;
    border: 1px solid var(--border-color) !important;
}
.stCodeBlock code {
    color: var(--text-heading) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
    background: transparent !important;
}

/* Search / Chat Input */
div[data-testid="stChatInput"] {
    background: transparent !important;
    padding-bottom: 24px !important;
}

div[data-testid="stChatInput"] > div {
    background: var(--card-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    box-shadow: var(--shadow-sm) !important;
    padding: 4px !important;
}

div[data-testid="stChatInput"] > div:focus-within {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 1px var(--primary-color) !important;
}

/* Send Button */
[data-testid="stChatInputSubmitButton"] {
    background-color: var(--primary-color) !important;
    color: white !important;
    border-radius: 8px !important;
    width: 32px !important;
    height: 32px !important;
    margin-right: 8px !important;
    margin-bottom: 8px !important;
    transition: background 0.2s ease;
}
[data-testid="stChatInputSubmitButton"]:hover {
    background-color: var(--primary-hover) !important;
}

/* Avatars */
[data-testid="chatAvatarIcon-user"] {
    display: none !important; /* Hide user avatar for cleaner Question Title look */
}
[data-testid="chatAvatarIcon-assistant"] {
    background-color: var(--primary-color) !important;
    color: white !important;
    border-radius: 6px !important;
}
</style>
    """, unsafe_allow_html=True)
