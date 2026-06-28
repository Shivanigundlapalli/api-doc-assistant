import streamlit as st

def render_source_chips(sources: list, confidence: int = 0):
    """
    Renders source citations as native Streamlit popovers underneath the chat response.
    When clicked, they reveal the raw excerpt.
    """
    if not sources:
        return
        
    st.markdown("<div style='font-size: 13px; font-weight: 600; color: var(--text-muted); margin-top: 24px; margin-bottom: 12px; letter-spacing: 0.05em; text-transform: uppercase;'>Sources</div>", unsafe_allow_html=True)
    
    # Deduplicate sources based on filename
    unique_sources = {}
    for src in sources:
        if isinstance(src, dict):
            metadata = src.get("metadata", {})
            content = src.get("content", "")
        else:
            metadata = getattr(src, "metadata", {})
            content = getattr(src, "page_content", "")
            
        raw_name = metadata.get("source", metadata.get("name", "Unknown Source"))
        name = str(raw_name).split('/')[-1].split('\\')[-1]
        
        if name not in unique_sources:
            unique_sources[name] = {"chunks": []}
        
        # Avoid perfectly identical chunks
        if content not in unique_sources[name]["chunks"]:
            unique_sources[name]["chunks"].append(content)
    
    # Render inline popovers using columns so they appear side-by-side
    if unique_sources and isinstance(unique_sources, dict):
        cols = st.columns(len(unique_sources) + 1)
        for idx, (name, data) in enumerate(unique_sources.items()):
        
            # Heuristics for a clean title and section
            title = name.replace(".md", "").replace("-", " ").replace("_", " ").title()
            
            # Determine Confidence String
            conf_str = "High" if confidence >= 80 else ("Medium" if confidence >= 40 else "Low")
            
            with cols[idx]:
                with st.popover(f"📄 {name}"):
                    st.markdown(f"**Retrieved From**")
                    st.markdown(f"{name}")
                    st.markdown(f"Section: {title}")
                    st.markdown(f"Confidence: {conf_str}")
                    st.divider()
                    for chunk in data["chunks"]:
                        st.markdown(
                            f"<div style='background-color: var(--bg-secondary); padding: 16px; border-left: 3px solid var(--primary-color); border-radius: 8px; font-size: 14px; color: var(--text-primary); margin-bottom: 12px;'>{chunk}</div>", 
                            unsafe_allow_html=True
                        )

    # Action buttons below
    st.markdown(f"""
        <style>
            .enterprise-action-btn {{
                font-size: 14px; 
                padding: 6px 14px; 
                border-radius: 20px; 
                border: 1px solid var(--border-color); 
                background: var(--bg-card); 
                color: var(--text-secondary);
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                font-weight: 500;
                transition: all var(--transition-hover);
                box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            }}
            .enterprise-action-btn:hover {{
                background: var(--bg-secondary);
                border-color: var(--text-disabled);
                color: var(--text-primary);
                transform: translateY(-1px);
            }}
            .enterprise-action-btn:active {{
                transform: translateY(0);
            }}
        </style>
        <div class="action-buttons-wrapper animated-fade" style="margin-top: 24px; display: flex; gap: 8px; flex-wrap: wrap; border-top: 1px solid var(--border-color); padding-top: 16px;">
            <button class="enterprise-action-btn" onclick="navigator.clipboard.writeText('Response copied!')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                Copy
            </button>
            <button class="enterprise-action-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>
                Helpful
            </button>
            <button class="enterprise-action-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"></path></svg>
                Not Helpful
            </button>
            <button class="enterprise-action-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path></svg>
                Regenerate
            </button>
            <button class="enterprise-action-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                View Sources
            </button>
            <button class="enterprise-action-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                Download Markdown
            </button>
        </div>
    """, unsafe_allow_html=True)
    
    return sources

