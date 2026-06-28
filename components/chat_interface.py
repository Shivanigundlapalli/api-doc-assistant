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
    
    # Render inline popovers using CSS flexbox for perfect responsiveness
    if unique_sources and isinstance(unique_sources, dict):
        with st.container():
            st.markdown('<div class="source-chips-hook"></div>', unsafe_allow_html=True)
            for idx, (name, data) in enumerate(unique_sources.items()):
                # Heuristics for a clean title and section
                title = name.replace(".md", "").replace("-", " ").replace("_", " ").title()
                
                # Determine Confidence String
                conf_str = "High" if confidence >= 80 else ("Medium" if confidence >= 40 else "Low")
                
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
            /* Responsive Flexbox wrapper for Source Chips */
            div[data-testid="stVerticalBlock"]:has(.source-chips-hook) {{
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: wrap !important;
                gap: 12px !important;
                align-items: center !important;
            }}
            div[data-testid="stVerticalBlock"]:has(.source-chips-hook) > div[data-testid="stElementContainer"] {{
                width: auto !important;
                flex: 0 0 auto !important;
            }}
            div[data-testid="stVerticalBlock"]:has(.source-chips-hook) > div[data-testid="stElementContainer"]:has(.source-chips-hook) {{
                display: none !important;
            }}

            /* Source Card Overrides */
            div[data-testid="stPopover"] > button {{
                width: max-content !important;
                min-width: 140px !important;
                max-width: 250px !important;
                height: 48px !important;
                padding: 0 12px !important;
                border-radius: 12px !important;
                background-color: var(--bg-card) !important;
                border: 1px solid var(--border-color) !important;
                box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
                transition: all 0.2s ease !important;
                display: flex !important;
                align-items: center !important;
                justify-content: flex-start !important;
                overflow: hidden !important;
            }}
            div[data-testid="stPopover"] > button div[data-testid="stMarkdownContainer"] {{
                width: 100% !important;
                overflow: hidden !important;
            }}
            div[data-testid="stPopover"] > button p {{
                font-size: 13px !important;
                font-weight: 500 !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
                margin: 0 !important;
                color: var(--text-primary) !important;
                text-align: left !important;
                width: 100% !important;
            }}
            div[data-testid="stPopover"] > button:hover {{
                border-color: var(--primary-color) !important;
                background-color: var(--bg-secondary) !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
            }}

            /* Action Buttons Overrides */
            .enterprise-action-btn {{
                font-size: 13px; 
                height: 40px;
                padding: 0 16px; 
                border-radius: 8px; 
                border: 1px solid var(--border-color); 
                background: #FFFFFF; 
                color: var(--text-secondary);
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                font-weight: 500;
                transition: all 0.2s ease;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
            }}
            .enterprise-action-btn:hover {{
                background: #F9FAFB;
                border-color: #D1D5DB;
                color: var(--text-primary);
                transform: translateY(-1px);
                box-shadow: 0 4px 6px rgba(0,0,0,0.04);
            }}
            .enterprise-action-btn:active {{
                transform: translateY(0);
            }}
        </style>
        <div class="action-buttons-wrapper animated-fade" style="margin-top: 32px; display: flex; gap: 8px; flex-wrap: wrap; border-top: 1px solid var(--border-color); padding-top: 24px;">
            <button class="enterprise-action-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                <span>Copy</span>
            </button>
            <button class="enterprise-action-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>
                <span>Helpful</span>
            </button>
            <button class="enterprise-action-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"></path></svg>
                <span>Not Helpful</span>
            </button>
            <button class="enterprise-action-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path></svg>
                <span>Regenerate</span>
            </button>
            <button class="enterprise-action-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                <span>View Sources</span>
            </button>
            <button class="enterprise-action-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                <span>Download Markdown</span>
            </button>
        </div>
    """, unsafe_allow_html=True)
    
    import streamlit.components.v1 as components
    components.html("""
        <script>
            const parent = window.parent.document;
            const wrappers = parent.querySelectorAll('.action-buttons-wrapper');
            if (wrappers.length > 0) {
                const latest = wrappers[wrappers.length - 1];
                if (!latest.dataset.bound) {
                    latest.dataset.bound = "true";
                    const btns = latest.querySelectorAll('.enterprise-action-btn');
                    
                    btns.forEach(btn => {
                        btn.addEventListener('click', function(e) {
                            e.preventDefault();
                            
                            const origHTML = this.innerHTML;
                            const type = this.innerText.toLowerCase();
                            const chatMsg = this.closest('.stChatMessage');
                            let msgText = chatMsg ? chatMsg.querySelector('[data-testid="stMarkdownContainer"]').innerText : "";
                            
                            const showMsg = (msg) => {
                                this.innerHTML = `<span style="font-size:12px; font-weight:500; display:flex; align-items:center; justify-content:center; width:100%; height:100%;">${msg}</span>`;
                                setTimeout(() => this.innerHTML = origHTML, 2000);
                            };
                            
                            if (type.includes('copy')) {
                                navigator.clipboard.writeText(msgText).then(() => showMsg('✅ Copied'));
                            } else if (type.includes('not helpful')) {
                                showMsg('Will improve!');
                            } else if (type.includes('helpful')) {
                                showMsg('✅ Thanks!');
                            } else if (type.includes('regenerate')) {
                                showMsg('Submit again 👆');
                            } else if (type.includes('sources')) {
                                showMsg('👆 Sources above');
                            } else if (type.includes('download')) {
                                const blob = new Blob([msgText], {type: 'text/markdown'});
                                const url = URL.createObjectURL(blob);
                                const a = parent.createElement('a');
                                a.href = url;
                                a.download = 'response.md';
                                parent.body.appendChild(a);
                                a.click();
                                parent.body.removeChild(a);
                                URL.revokeObjectURL(url);
                                showMsg('✅ Downloaded');
                            }
                        });
                    });
                }
            }
        </script>
    """, height=0)
    
    return sources

