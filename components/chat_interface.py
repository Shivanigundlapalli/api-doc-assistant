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
        
    # Render Collapsible Source Cards at top layer
    active_sources = render_source_chip(sources, developer_mode=False)
    
    # 4. More Details Expander (Nests all complex info)
    has_details = parsed.get("explanation") or parsed.get("steps") or parsed.get("warnings") or parsed.get("related")
    
    if has_details:
        with st.expander("🔍 More Details", expanded=False):
            if parsed.get("explanation"):
                st.markdown("**Detailed Explanation**")
                st.markdown(parsed["explanation"])
                
            if parsed.get("steps"):
                st.markdown("**Developer Actions**")
                st.markdown(parsed["steps"])
                
            if parsed.get("warnings"):
                st.markdown("**Edge Cases & Warnings**")
                st.warning(parsed["warnings"], icon="⚠️")
                
            if parsed.get("related"):
                st.markdown("**Related Documentation**")
                st.markdown(parsed["related"])
        
    # 5. Action Bar
    st.markdown("""
        <div style="margin-top: 16px; display: flex; gap: 8px;">
            <button class="btn-action">📋 Copy Answer</button>
            <button class="btn-action">🔗 Share</button>
            <button class="btn-action">👍</button>
            <button class="btn-action">👎</button>
        </div>
    """, unsafe_allow_html=True)
    
    return active_sources
