import streamlit as st

def render_source_chips(sources: list):
    """
    Renders source citations as native Streamlit popovers underneath the chat response.
    When clicked, they reveal the raw excerpt.
    """
    if not sources:
        return
        
    st.markdown("<div style='font-size: 0.85rem; font-weight: 600; color: #666; margin-top: 15px; margin-bottom: 8px;'>Sources</div>", unsafe_allow_html=True)
    
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
    cols = st.columns(len(unique_sources) + 1)
    for idx, (name, data) in enumerate(unique_sources.items()):
        with cols[idx]:
            with st.popover(f"📄 {name}"):
                for chunk in data["chunks"]:
                    st.markdown(chunk)
                    st.divider()

    # Action buttons below
    st.markdown(f"""
        <div class="action-buttons-wrapper" style="margin-top: 12px; display: flex; gap: 8px;">
            <button class="action-btn" onclick="navigator.clipboard.writeText('Response copied!')" style="font-size: 0.75rem; padding: 4px 8px; border-radius: 4px; border: 1px solid #ccc; background: transparent; cursor: pointer;">📋 Copy Answer</button>
            <button class="action-btn" style="font-size: 0.75rem; padding: 4px 8px; border-radius: 4px; border: 1px solid #ccc; background: transparent; cursor: pointer;">👍 Helpful</button>
            <button class="action-btn" style="font-size: 0.75rem; padding: 4px 8px; border-radius: 4px; border: 1px solid #ccc; background: transparent; cursor: pointer;">👎 Not Helpful</button>
        </div>
    """, unsafe_allow_html=True)
    
    return sources
