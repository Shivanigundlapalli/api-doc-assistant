import streamlit as st

def inject_custom_css():
    """
    Injects custom CSS to transform Streamlit into a modern enterprise SaaS application.
    Implements a 10/10 production standard presentation comparable to Stripe/OpenAI Docs.
    """
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg-main: #FAF8F7;
    --bg-secondary: #F2ECEC;
    --bg-card: #FFFFFF;
    --bg-sidebar: #F7F3F3;
    
    --primary-color: #6D122B;
    --primary-hover: #5B1024;
    --primary-dark: #4A0D1D;
    --primary-accent: #8C1C3A;
    --primary-light: #FCF7F8;
    
    --text-primary: #1E1E1E;
    --text-secondary: #5F5F5F;
    --text-muted: #7A7A7A;
    --text-disabled: #A7A7A7;
    
    --border-color: #E8DADA;
    
    --success: #2E8B57;
    --warning: #D97706;
    --error: #DC2626;
    --info: #2563EB;
    
    --shadow-card: 0 8px 30px rgba(0,0,0,.05);
    --border-radius-base: 16px;
    
    --transition-fade: 200ms ease;
    --transition-hover: 150ms ease;
}

/* Global Typography & Spacing */
html, body, [class*="css"], .stMarkdown p, .stMarkdown li {
    font-family: 'Inter', sans-serif !important;
    font-weight: 400;
    color: var(--text-secondary);
}

/* Headings Base */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    letter-spacing: -0.01em !important;
}

h1 { 
    font-size: 48px !important; 
    font-weight: 700 !important;
    color: #2B1020 !important;
    margin-bottom: 24px !important; 
}
h2 { 
    font-size: 32px !important; 
    font-weight: 600 !important;
    margin-top: 36px !important; 
    padding-top: 16px !important;
    margin-bottom: 24px !important; 
    color: var(--text-primary) !important;
}
h3 { 
    font-size: 16px !important; 
    font-weight: 600 !important;
    color: var(--text-primary) !important;
}

/* Remove top border from the very first h2 in a message */
.stChatMessage .stMarkdown > div > h2:first-of-type {
    border-top: none !important;
    padding-top: 0 !important;
    margin-top: 0 !important;
}

/* Section Decorators */
h2#direct-answer { border-left: 4px solid var(--primary-color); display: block; padding-left: 12px; padding-top: 0; }
h2#explanation, h2#steps, h2#code-example, h2#example, h2#best-practices, h2#common-errors, h2#related-documentation, h2#sources {
    color: var(--text-primary) !important;
}

/* Steps: Modern numbered list */
ol {
    list-style: none;
    counter-reset: my-awesome-counter;
    padding-left: 0 !important;
}
ol > li {
    counter-increment: my-awesome-counter;
    position: relative;
    padding-left: 2rem !important;
    margin-bottom: 0.5rem;
}
ol > li::before {
    content: counter(my-awesome-counter);
    position: absolute;
    left: 0;
    top: 2px;
    font-weight: 600;
    color: var(--primary-color);
    background: var(--primary-light);
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
}

/* Center Container max width */
.main .block-container {
    max-width: 1050px !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding-top: 2rem !important;
    padding-bottom: 5rem !important;
}

/* Sidebar styling overrides */
[data-testid="stSidebar"] {
    width: 280px !important;
    min-width: 280px !important;
    max-width: 280px !important;
    border-right: 1px solid var(--border-color) !important;
}

/* Sidebar Chat Buttons */
[data-testid="stSidebar"] button[kind="secondary"] {
    background-color: #FFFFFF !important;
    border: 1px solid transparent !important;
    border-radius: 14px !important;
    color: var(--text-primary) !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
    padding: 10px 14px !important;
    margin-bottom: 8px !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    transition: all var(--transition-hover) !important;
    justify-content: flex-start !important;
    height: auto !important;
    min-height: 44px !important;
}
[data-testid="stSidebar"] button[kind="secondary"] p {
    font-size: 14px !important;
}
[data-testid="stSidebar"] button[kind="secondary"]:hover {
    border-color: var(--primary-color) !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
}

/* Sidebar New Chat Button */
[data-testid="stSidebar"] button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-accent)) !important;
    border: none !important;
    color: white !important;
    border-radius: 14px !important;
    font-weight: 500 !important;
    padding: 12px !important;
    width: 100% !important;
    transition: all var(--transition-hover) !important;
    box-shadow: 0 10px 30px rgba(109, 18, 43, 0.25) !important;
}
[data-testid="stSidebar"] button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 12px 35px rgba(109, 18, 43, 0.3) !important;
}

/* Hide Default Streamlit Elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header { background: transparent !important; }

/* Chat Messages */
.stChatMessage {
    padding: 0 !important;
    background: transparent !important;
    width: 100% !important;
    margin: 0 auto 32px auto !important;
}

/* Avatar Container Layout */
[data-testid="stChatMessageAvatar"] {
    display: flex !important;
    align-items: flex-start !important;
    justify-content: center !important;
    width: 40px !important;
    height: 40px !important;
    min-width: 40px !important;
    margin-right: 16px !important;
}

[data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] {
    width: 40px !important;
    height: 40px !important;
    border-radius: 50% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Hide default streamlit SVGs */
[data-testid="chatAvatarIcon-user"] svg, [data-testid="chatAvatarIcon-assistant"] svg {
    display: none !important;
}

/* User Avatar Styling */
[data-testid="chatAvatarIcon-user"] {
    background-color: #FDEBED !important;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%236D122B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>');
    background-repeat: no-repeat;
    background-position: center;
}

/* Assistant Avatar Styling */
[data-testid="chatAvatarIcon-assistant"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E8DADA !important;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%236D122B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/><path d="M12 8V4H8"/></svg>');
    background-repeat: no-repeat;
    background-position: center;
}

/* Force message content container to use full width */
div[data-testid="stChatMessageContent"] {
    width: 100% !important;
}

/* Align user row vertically */
.stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
    align-items: center !important;
}

/* Assistant Message Bubble (White Card) */
.stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
    background-color: var(--bg-card) !important;
    border-radius: 18px !important;
    border: 1px solid var(--border-color) !important;
    box-shadow: var(--shadow-card) !important;
    padding: 28px !important;
    transition: transform var(--transition-hover), box-shadow var(--transition-hover) !important;
}
.stChatMessage[data-testid="stChatMessage"]:nth-child(even):hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0,0,0,.08) !important;
}

/* User Message Bubble */
.stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
    background-color: var(--primary-light) !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 20px !important;
    padding: 16px 24px !important;
}

.stChatMessage[data-testid="stChatMessage"]:nth-child(odd) p {
    font-size: 16px !important;
    font-weight: 500 !important;
    color: var(--primary-color) !important;
    margin: 0 !important;
    background-color: transparent !important;
}

/* NOTES / BEST PRACTICES - Subtle Info Card */
h2#best-practices + ul, h2#best-practices + p,
h2#common-errors + ul, h2#common-errors + p,
h2#explanation + p {
    background-color: var(--bg-card) !important;
    border-left: 4px solid var(--info) !important;
    border-radius: 8px !important;
    padding: 16px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
    border: 1px solid var(--border-color);
}

/* INLINE CODE */
code:not(pre code) {
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 14px !important;
    border: 1px solid var(--border-color) !important;
}

/* CODE BLOCKS */
.stCodeBlock {
    background-color: var(--bg-secondary) !important;
    border-radius: 8px !important;
    margin-top: 16px !important;
    margin-bottom: 24px !important;
    border: 1px solid var(--border-color) !important;
}
.stCodeBlock code {
    color: var(--text-primary) !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
    background: transparent !important;
}

/* Search / Chat Input */
div[data-testid="stChatInput"] {
    background: transparent !important;
    padding-bottom: 24px !important;
}

div[data-testid="stChatInput"] > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 18px !important;
    height: 60px !important;
    padding: 6px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02) !important;
    transition: all var(--transition-hover) !important;
}

div[data-testid="stChatInput"] > div:focus-within {
    border-color: var(--primary-accent) !important;
    box-shadow: 0 0 0 3px rgba(140, 28, 58, 0.15) !important;
}

div[data-testid="stChatInput"] textarea {
    background-color: transparent !important;
    color: var(--text-primary) !important;
    font-size: 16px !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-muted) !important;
    font-size: 16px !important;
}

/* Send Button */
[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-accent)) !important;
    border: none !important;
    color: white !important;
    border-radius: 50% !important;
    width: 44px !important;
    height: 44px !important;
    margin-right: 2px !important;
    margin-bottom: 2px !important;
    transition: transform var(--transition-hover) !important;
}
[data-testid="stChatInputSubmitButton"]:hover {
    transform: scale(1.05) !important;
}
[data-testid="stChatInputSubmitButton"] svg {
    fill: white !important;
    color: white !important;
}

/* Avatars (Hidden in earlier rule) */

/* Animations */
.animated-fade {
    animation: fadeIn var(--transition-fade);
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}

</style>
    """, unsafe_allow_html=True)

