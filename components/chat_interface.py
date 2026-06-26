import streamlit as st

def render_source_chip(sources: list, developer_mode: bool = False):
    """
    Renders source cards based on Stripe Docs / Notion AI aesthetic.
    Returns the unique sources so they can be shown in the Right Context Panel if needed.
    """
    if not sources:
        return []
        
    # Get unique source files
    unique_sources = {}
    for doc in sources:
        src = doc.metadata.get('source', 'Unknown File').split('/')[-1].split('\\')[-1]
        if src not in unique_sources:
            unique_sources[src] = []
        unique_sources[src].append(doc)
    
    st.markdown("### 📄 Sources")
    
    # Render Enterprise Source Cards
    cols = st.columns(min(len(unique_sources), 3)) # Max 3 columns for sources
    
    for idx, (src_name, chunks) in enumerate(list(unique_sources.items())[:3]): # Show top 3
        with cols[idx]:
            st.markdown(f"""
                <div style="background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; height: 100%;">
                    <div style="font-weight: 600; font-size: 0.9rem; color: var(--text-primary); margin-bottom: 4px;">📄 {src_name}</div>
                    <div style="font-size: 0.75rem; color: var(--success-color); margin-bottom: 4px;">Relevance: High</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 8px;">Updated: Today</div>
                    <a href="#" style="font-size: 0.8rem; color: var(--primary-color); text-decoration: none;">[View Source]</a>
                </div>
            """, unsafe_allow_html=True)

    if developer_mode:
        with st.expander("Developer Debug (Chunks)", expanded=False):
            for src_name, chunks in unique_sources.items():
                for i, doc in enumerate(chunks):
                    st.json(doc.metadata)
                    st.markdown(f"```text\n{doc.page_content}\n```")

    st.markdown("<br>", unsafe_allow_html=True)
    return list(unique_sources.keys())

def render_enterprise_answer(parsed: dict, sources: list, msg_index: int = 0):
    """
    Renders the parsed structured LLM response into an Enterprise SaaS layout.
    Matches the provided mockup styling perfectly.
    """
    # 1. Header & Confidence
    if parsed.get("confidence"):
        st.markdown(f"""
            <div style='display: flex; justify-content: flex-end; margin-bottom: 10px;'>
                <span style='font-size: 0.75rem; color: #666; display: flex; align-items: center; gap: 6px;'>
                    Confidence: <span style='color: #48BB78;'>●</span> {parsed['confidence']}
                </span>
            </div>
        """, unsafe_allow_html=True)
        
    # 2. Main Answer
    if parsed.get("answer"):
        st.markdown(parsed["answer"])

    # 3. Code Snippets
    if parsed.get("code_snippets"):
        for code in parsed["code_snippets"]:
            st.code(code.get("code", ""), language=code.get("language", "text"))

    # 4. Sources (Pill shaped inline chips)
    active_sources = []
    if sources:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 600; color: #333; margin-top: 15px; margin-bottom: 8px;'>📄 Sources</div>", unsafe_allow_html=True)
        
        sources_html = ""
        for src in sources:
            if isinstance(src, dict):
                metadata = src.get("metadata", {})
            else:
                metadata = getattr(src, "metadata", {})
                
            raw_name = metadata.get("source", metadata.get("name", "Unknown Source"))
            name = str(raw_name).split('/')[-1].split('\\')[-1]
            url = metadata.get("url", "#")
            
            active_sources.append(name)
            sources_html += f"<a href='{url}' target='_blank' class='source-chip'>📄 {name} ↗</a>"
            
        st.markdown(sources_html, unsafe_allow_html=True)

    # 5. Related Content
    if parsed.get("related"):
        st.markdown("<div style='font-size: 0.85rem; font-weight: 600; color: #333; margin-top: 15px; margin-bottom: 8px;'>Related</div>", unsafe_allow_html=True)
        st.markdown(parsed["related"])
        
    # 6. Action Bar (Flexbox layout)
    st.markdown(f"""
        <div class="action-buttons-wrapper">
            <button class="action-btn" onclick="window.parent.postMessage({{type: 'copy', text: 'answer'}})">📋 Copy Answer</button>
            <button class="action-btn" onclick="window.parent.postMessage({{type: 'share'}})">↗ Share</button>
            <button class="action-btn" onclick="window.parent.postMessage({{type: 'helpful'}})">👍 Helpful</button>
            <button class="action-btn" onclick="window.parent.postMessage({{type: 'unhelpful'}})">👎 Not Helpful</button>
        </div>
    """, unsafe_allow_html=True)
    
    return sources
