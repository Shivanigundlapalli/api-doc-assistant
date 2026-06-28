import streamlit as st

def render_hero():
    """
    Renders the hero section and initial search box for the empty state.
    """
    st.markdown("""
        <div class="hero-container animated-fade" style="text-align: left; margin-top: 5rem; margin-bottom: 4rem;">
            <h1 class="hero-title" style="font-size: 48px; font-weight: 700; color: #2B1020; margin-bottom: 16px; letter-spacing: -0.02em;">Ask anything about your documentation</h1>
            <p class="hero-subtitle" style="font-size: 16px; color: #6B7280; line-height: 1.7; max-width: 600px; margin: 0;">Get answers, code examples, troubleshooting guidance, and API explanations.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Suggested prompts
    btn_style = "background-color: #FFFFFF; color: var(--primary-color); border: 1px solid var(--border-color); border-radius: 20px; padding: 10px 18px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all var(--transition-hover);"
    hover_js = "onmouseover=\"this.style.backgroundColor='var(--primary-color)'; this.style.color='#FFFFFF'\" onmouseout=\"this.style.backgroundColor='#FFFFFF'; this.style.color='var(--primary-color)'\""
    
    st.markdown(f"""
        <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 3rem; justify-content: flex-start;" class="animated-fade">
            <button style="{btn_style}" {hover_js} onclick="document.querySelector('input').value='How do I authenticate?';">
                How do I authenticate?
            </button>
            <button style="{btn_style}" {hover_js} onclick="document.querySelector('input').value='What are the rate limits?';">
                What are the rate limits?
            </button>
            <button style="{btn_style}" {hover_js} onclick="document.querySelector('input').value='Show Python examples';">
                Show Python examples
            </button>
            <button style="{btn_style}" {hover_js} onclick="document.querySelector('input').value='Explain 401 Unauthorized';">
                Explain 401 Unauthorized
            </button>
        </div>
    """, unsafe_allow_html=True)
