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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Render Collapsible Source Cards
    with st.expander(f"📄 Sources ({len(unique_sources)})", expanded=False):
        for src_name, chunks in unique_sources.items():
            st.markdown(f"**{src_name}**")
            st.caption(f"{len(chunks)} relevant sections retrieved • [View Source]")
            
            if developer_mode:
                for i, doc in enumerate(chunks):
                    st.caption(f"Chunk {i+1}")
                    st.json(doc.metadata)
                    st.markdown(f"```text\n{doc.page_content}\n```")
            st.divider()

            st.divider()

    return list(unique_sources.keys())

def render_enterprise_answer(parsed: dict, sources: list):
    """
    Renders the parsed structured LLM response into an Enterprise SaaS layout.
    """
    # 1. Header & Confidence
    if parsed.get("confidence"):
        st.markdown(f"**Confidence:** {parsed['confidence']}")
        
    # 2. Quick Answer Card
    if parsed.get("quick_answer"):
        st.markdown(f"""
            <div class="quick-answer-card">
                <div class="qa-title">✅ Quick Answer</div>
                <div>{parsed['quick_answer']}</div>
            </div>
        """, unsafe_allow_html=True)
        
    # 3. Code Examples
    if parsed.get("code"):
        st.markdown("### 💻 Code Example")
        st.markdown(parsed["code"])
        
    # 4. Detailed Explanation
    if parsed.get("explanation"):
        with st.expander("▼ Detailed Explanation", expanded=False):
            st.markdown(parsed["explanation"])
            
    # 5. Steps
    if parsed.get("steps"):
        st.markdown("### 🚀 Getting Started")
        st.markdown(parsed["steps"])
        
    # 6. Warnings
    if parsed.get("warnings"):
        st.warning(parsed["warnings"], icon="⚠️")
        
    # 7. Action Bar
    st.markdown("""
        <div style="margin-top: 24px; display: flex; gap: 12px;">
            <button class="btn-action">📋 Copy Answer</button>
            <button class="btn-action">🔗 Share</button>
            <button class="btn-action">⬇ Export PDF</button>
            <button class="btn-action">👍</button>
            <button class="btn-action">👎</button>
        </div>
    """, unsafe_allow_html=True)
    
    # Render Sources natively
    return render_source_chip(sources, developer_mode=False)
