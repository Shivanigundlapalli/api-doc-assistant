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

    return list(unique_sources.keys())
