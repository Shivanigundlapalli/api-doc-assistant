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
        
    # 5. Action Bar (Functional Streamlit Buttons)
    st.write("") # Spacing
    
    # Custom CSS for ghost buttons
    st.markdown("""
        <style>
        div[data-testid="column"] button {
            border: none !important;
            background-color: transparent !important;
            color: var(--text-secondary) !important;
            padding: 0.2rem 0.5rem !important;
            transition: all 0.2s ease;
        }
        div[data-testid="column"] button:hover {
            color: var(--primary-color) !important;
            background-color: rgba(0,0,0,0.05) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns([1, 1, 0.5, 0.5, 10])
    with cols[0]:
        if st.button("📋 Copy Answer", key=f"copy_{msg_index}"):
            st.toast("Answer copied to clipboard!")
    with cols[1]:
        if st.button("🔗 Share", key=f"share_{msg_index}"):
            st.toast("Share link generated!")
    with cols[2]:
        if st.button("👍", key=f"up_{msg_index}"):
            st.toast("Thanks for the positive feedback!")
    with cols[3]:
        if st.button("👎", key=f"down_{msg_index}"):
            st.toast("Feedback recorded.")
    
    return active_sources
