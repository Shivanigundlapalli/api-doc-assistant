import streamlit as st

def render_hero():
    """
    Renders the hero section and initial search box for the empty state.
    """
    st.markdown("""
        <div class="hero-container animated-fade">
            <h1 class="hero-title">Ask anything about your documentation</h1>
            <p class="hero-subtitle">Get answers, code examples, troubleshooting guidance, and API explanations.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Suggested prompts
    st.markdown("""
        <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 2rem;" class="animated-fade">
            <button class="prompt-pill" onclick="document.querySelector('input').value='How do I authenticate?';">
                🔑 How do I authenticate?
            </button>
            <button class="prompt-pill" onclick="document.querySelector('input').value='What are the rate limits?';">
                ⏱️ What are the rate limits?
            </button>
            <button class="prompt-pill" onclick="document.querySelector('input').value='Fix 401 Unauthorized';">
                🐛 Fix 401 Unauthorized
            </button>
            <button class="prompt-pill" onclick="document.querySelector('input').value='Show code examples';">
                💻 Show code examples
            </button>
            <button class="prompt-pill" onclick="document.querySelector('input').value='Explain this error';">
                ⚠️ Explain this error
            </button>
        </div>
    """, unsafe_allow_html=True)
