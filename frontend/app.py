# app.py
import streamlit as st
import pandas as pd
import re
import os
import time
from pathlib import Path
from datetime import datetime
from io import StringIO

# ─── Your backend imports ───────────────────────────────────────────────────
from backend.config import (
    MAX_FILE_SIZE_MB, TEXT_BASED_THRESHOLD_CHARS,
    OCR_LANG, OCR_PREFERRED_PSMS, FUZZY_MATCH_THRESHOLD
)
from backend.utils import (
    save_uploaded_file, cleanup_temp_file, get_context,
    init_db, save_processed, get_processed_files
)
from backend.pdf_processor import PDFProcessor
from backend.search_engine import SearchEngine

init_db()

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multilingual OCR PDF Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Title & Subtitle ───────────────────────────────────────────────────────
st.title("Multilingual OCR PDF Search")
st.caption("Telugu + Urdu • Scanned & Digital PDFs • Exact + Fuzzy Matching • ~70–75% Prototype")

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Controls")
    
    st.markdown("### Quick Stats")
    history = get_processed_files()
    st.metric("Processed Files", len(history))
    st.metric("Last Processed", history[0]["date"][:16] if history else "—")
    
    st.markdown("---")
    
    with st.expander("Display Options", expanded=True):
        show_full_pages = st.checkbox("Show full page previews", value=True)
        highlight_color = st.color_picker("Highlight color", "#ffff99")
        max_results_show = st.slider("Max results to expand", 3, 20, 8)
    
    with st.expander("About", expanded=False):
        st.caption("Project: Multilingual OCR-Based PDF Search System")
        st.caption("Focus: Telugu & Urdu")
        st.caption("Features: Type detection • Preprocessing • Fuzzy search • Export")
        st.caption("Status: ~70% complete")

# ─── Top metrics row ────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Supported Languages", "Telugu + Urdu")
col2.metric("Search Types", "Exact + Fuzzy")
col3.metric("OCR Confidence Goal", ">75%")
col4.metric("Max File Size", f"{MAX_FILE_SIZE_MB} MB")

st.markdown("---")

# ─── Main Tabs ──────────────────────────────────────────────────────────────
tab_quick, tab_batch, tab_history = st.tabs([
    "📄  Quick Search",
    "📑  Batch / Multi-file",
    "📊  History & Stats"
])

processor = PDFProcessor()
engine = SearchEngine()

# ─── QUICK SEARCH TAB ───────────────────────────────────────────────────────
with tab_quick:
    st.subheader("Search in Single Document")
    
    c1, c2 = st.columns([5, 3])
    
    with c1:
        uploaded_file = st.file_uploader(
            "Upload PDF (scanned or text-based)",
            type="pdf",
            help="Supports Telugu & Urdu in both unicode and image-based PDFs"
        )
    
    with c2:
        keywords_input = st.text_input(
            "Keywords (comma separated)",
            placeholder="రామాయణం, کتاب, పుస్తకం, राम",
            key="quick_keywords"
        )
    
    search_triggered = st.button("🔍  Start Search", type="primary", use_container_width=True)

    if search_triggered and uploaded_file and keywords_input.strip():
        with st.status("Processing document...", expanded=True) as status:
            try:
                status.update(label="Saving file...", state="running")
                filepath = save_uploaded_file(uploaded_file)
                
                status.update(label="Detecting PDF type...", state="running")
                page_data, source = processor.process_pdf(filepath)
                
                full_text = " ".join(text for _, text, _ in page_data)
                save_processed(uploaded_file.name, len(page_data), source, len(full_text))
                
                status.update(label="Searching keywords...", state="running")
                keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
                results = engine.search_keywords(page_data, keywords, source, uploaded_file.name)
                
                status.update(label=f"Found {len(results)} matches", state="complete")
                time.sleep(0.6)
                
                if results:
                    st.success(f"**{len(results)} matches found**  •  {source.upper()} source  •  {len(page_data)} pages")
                    
                    # Result cards
                    for i, r in enumerate(results):
                        if i >= max_results_show:
                            st.caption(f"... {len(results) - max_results_show} more matches hidden")
                            break
                            
                        with st.expander(
                            f"Page {r['page']}  •  {r['keyword']}  •  {r['match_type'].upper()}  •  score {r['score']:.0f}",
                            expanded=(i < 3)
                        ):
                            cols = st.columns([4, 1])
                            cols[0].markdown(
                                f"**Matched:** {r['match']}\n\n"
                                f"{r['context']}"
                            )
                            cols[1].caption(f"conf {r['page_conf']:.1f}%")
                    
                    if show_full_pages:
                        with st.expander("Full Pages with Highlights", expanded=False):
                            for page_num, text, conf in page_data[:6]:  # limit for performance
                                h_text = text
                                page_results = [r for r in results if r["page"] == page_num]
                                for r in page_results:
                                    h_text = re.sub(
                                        f"({re.escape(r['match'])})",
                                        f"<mark style='background:{highlight_color}; padding:2px 4px'>\g<1></mark>",
                                        h_text,
                                        flags=re.IGNORECASE
                                    )
                                st.markdown(f"**Page {page_num}** (conf {conf:.1f}%)  \n{h_text}", unsafe_allow_html=True)
            
            except Exception as e:
                status.update(label=f"Error: {str(e)}", state="error")
            finally:
                if 'filepath' in locals():
                    cleanup_temp_file(filepath)

# ─── BATCH SEARCH TAB ───────────────────────────────────────────────────────
with tab_batch:
    st.subheader("Search Across Multiple Documents")
    
    uploaded_files = st.file_uploader(
        "Upload one or more PDFs",
        type="pdf",
        accept_multiple_files=True,
        help="Process and search across all selected files at once"
    )
    
    batch_keywords = st.text_input(
        "Keywords for batch search",
        placeholder="Enter same keywords as above...",
        key="batch_keywords"
    )
    
    if st.button("🔍  Search All Files", type="primary") and uploaded_files and batch_keywords.strip():
        with st.status("Batch processing started...", expanded=True) as status:
            all_results = []
            keywords = [k.strip() for k in batch_keywords.split(",") if k.strip()]
            
            for idx, file in enumerate(uploaded_files):
                status.update(label=f"Processing {file.name} ({idx+1}/{len(uploaded_files)})", state="running")
                try:
                    path = save_uploaded_file(file)
                    pages, src = processor.process_pdf(path)
                    full = " ".join(t for _, t, _ in pages)
                    save_processed(file.name, len(pages), src, len(full))
                    
                    res = engine.search_keywords(pages, keywords, src, file.name)
                    all_results.extend(res)
                    
                    cleanup_temp_file(path)
                except Exception as e:
                    st.warning(f"Skipped {file.name}: {str(e)}")
            
            status.update(label=f"Completed • {len(all_results)} total matches", state="complete")
            
            if all_results:
                st.success(f"**Batch complete** — {len(all_results)} matches across {len(uploaded_files)} files")
                
                # Grouped result display
                for fname in set(r["filename"] for r in all_results):
                    file_results = [r for r in all_results if r["filename"] == fname]
                    with st.expander(f"{fname}  •  {len(file_results)} matches"):
                        for r in file_results[:8]:
                            st.markdown(
                                f"**Page {r['page']}** • {r['keyword']} • **{r['match']}**  \n"
                                f"{r['context']}  \n"
                                f"<small>conf {r['page_conf']:.1f}% • score {r['score']:.0f}</small>",
                                unsafe_allow_html=True
                            )
                        if len(file_results) > 8:
                            st.caption(f"... and {len(file_results)-8} more")

# ─── HISTORY TAB ────────────────────────────────────────────────────────────
with tab_history:
    st.subheader("Processing History")
    
    if history:
        df_history = pd.DataFrame(history)
        st.dataframe(
            df_history[["filename", "date", "source", "pages"]],
            column_config={
                "filename": "Document",
                "date": st.column_config.DatetimeColumn("Processed", format="D MMM YYYY • h:mm a"),
                "source": st.column_config.TextColumn("Type"),
                "pages": st.column_config.NumberColumn("Pages")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No documents processed yet.", icon="📭")

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")