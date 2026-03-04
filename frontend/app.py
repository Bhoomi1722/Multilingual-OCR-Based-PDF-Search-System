# app.py
import streamlit as st
import pandas as pd
import re
import os
import time
from pathlib import Path
from datetime import datetime
from io import BytesIO

from backend.config import (
    MAX_FILE_SIZE_MB, TEXT_BASED_THRESHOLD_CHARS, MAX_PAGES_LIMIT,
    OCR_LANG, OCR_PREFERRED_PSMS, FUZZY_MATCH_THRESHOLD, UPLOAD_FOLDER
)
from backend.utils import (
    save_uploaded_file, cleanup_temp_file, get_context,
    init_db, save_processed, get_processed_files
)
from backend.pdf_processor import PDFProcessor
from backend.search_engine import SearchEngine

init_db()

st.set_page_config(
    page_title="Multilingual OCR PDF Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Multilingual OCR PDF Search")
st.caption("Telugu + Urdu • Scanned & Digital PDFs • Exact + Fuzzy Matching • ~80–85% Prototype")

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Controls")
    
    st.markdown("### Quick Stats")
    history = get_processed_files()
    st.metric("Processed Files", len(history))
    st.metric("Last Processed", history[0]["date"][:16] if history else "—")
    
    st.markdown("---")
    
    selected_lang = st.selectbox("Preferred Language", ["Auto-detect", "Telugu", "Urdu"])
    
    with st.expander("Display Options", expanded=True):
        show_full_pages = st.checkbox("Show full page previews", value=True)
        highlight_color = st.color_picker("Highlight color", "#ffff99")
        max_results_show = st.slider("Max results to expand", 3, 20, 8)
    
    with st.expander("About", expanded=False):
        st.caption("Project: Multilingual OCR-Based PDF Search System")
        st.caption("Telugu: Stable")
        st.caption("Urdu: Basic support added (EasyOCR fallback)")
        st.caption("Status: ~80–85% complete")

# ─── Top metrics ────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Supported Languages", "Telugu + Urdu")
col2.metric("Search Types", "Exact + Fuzzy")
col3.metric("OCR Confidence Goal", ">75%")
col4.metric("Max Pages (limit)", f"{MAX_PAGES_LIMIT}")

st.markdown("---")

# ─── Tabs ──────────────────────────────────────────────────────────────────
tab_quick, tab_batch, tab_cross, tab_history = st.tabs([
    "📄 Quick Search",
    "📑 Batch Upload",
    "🔎 Cross-File Search",
    "📊 History"
])

processor = PDFProcessor()
engine = SearchEngine()

# ─── QUICK SEARCH ──────────────────────────────────────────────────────────
with tab_quick:
    st.subheader("Single Document Search")
    
    c1, c2 = st.columns([5, 3])
    with c1:
        uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    with c2:
        keywords_input = st.text_input("Keywords (comma separated)", 
                                      placeholder="రామాయణం, کتاب, పుస్తకం")

    if st.button("🔍 Search", type="primary") and uploaded_file and keywords_input.strip():
        with st.status("Processing...", expanded=True) as status:
            try:
                filepath = save_uploaded_file(uploaded_file)
                page_data, source = processor.process_pdf(filepath)
                
                if len(page_data) > MAX_PAGES_LIMIT:
                    status.update(label=f"Limiting to first {MAX_PAGES_LIMIT} pages", state="running")
                    page_data = page_data[:MAX_PAGES_LIMIT]
                
                full_text = " ".join(text for _, text, _ in page_data)
                save_processed(uploaded_file.name, len(page_data), source, len(full_text))
                
                keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
                results = engine.search_keywords(page_data, keywords, source, uploaded_file.name)
                
                status.update(label=f"Found {len(results)} matches", state="complete")
                
                if results:
                    st.success(f"{len(results)} matches • {source.upper()} • {len(page_data)} pages")
                    
                    for i, r in enumerate(results[:max_results_show]):
                        with st.expander(f"Page {r['page']} • {r['keyword']} • {r['match_type']} • score {r['score']:.0f}"):
                            st.markdown(f"**Match:** {r['match']}")
                            st.markdown(r['context'])
                            st.caption(f"conf {r['page_conf']:.1f}%")
                    
                    if show_full_pages:
                        with st.expander("Full Pages Highlights"):
                            for page_num, text, conf in page_data[:8]:
                                h_text = text
                                for r in [r for r in results if r["page"] == page_num]:
                                    h_text = re.sub(
                                        f"({re.escape(r['match'])})",
                                        f"<mark style='background:{highlight_color}'>\\1</mark>",
                                        h_text, flags=re.I
                                    )
                                st.markdown(f"**Page {page_num}** (conf {conf:.1f}%)  \n{h_text}", unsafe_allow_html=True)
                
                # cleanup_temp_file(filepath)
            except Exception as e:
                status.update(label=f"Error: {str(e)}", state="error")

# ─── BATCH SEARCH ──────────────────────────────────────────────────────────
with tab_batch:
    st.subheader("Batch / Multi-file Search")
    
    uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
    batch_keywords = st.text_input("Keywords", key="batch_kw")
    
    if st.button("Search All", type="primary") and uploaded_files and batch_keywords:
        all_results = []
        keywords = [k.strip() for k in batch_keywords.split(",") if k.strip()]
        
        progress = st.progress(0)
        for i, file in enumerate(uploaded_files):
            try:
                path = save_uploaded_file(file)
                pages, src = processor.process_pdf(path)
                if len(pages) > MAX_PAGES_LIMIT:
                    pages = pages[:MAX_PAGES_LIMIT]
                full = " ".join(t for _, t, _ in pages)
                save_processed(file.name, len(pages), src, len(full))
                
                res = engine.search_keywords(pages, keywords, src, file.name)
                all_results.extend(res)
                # cleanup_temp_file(path)
            except Exception as e:
                st.warning(f"Skipped {file.name}: {e}")
            progress.progress((i+1)/len(uploaded_files))
        
        if all_results:
            df = pd.DataFrame([{
                "File": r["filename"],
                "Page": r["page"],
                "Keyword": r["keyword"],
                "Match": r["match"],
                "Type": r["match_type"],
                "Score": f"{r['score']:.1f}",
                "Context": r["context"]
            } for r in all_results])
            st.dataframe(df, use_container_width=True)

# ─── CROSS-FILE SEARCH ─────────────────────────────────────────────────────
with tab_cross:
    st.subheader("Cross-File Search (History)")
    
    history = get_processed_files()
    if not history:
        st.info("No processed files yet. Upload some PDFs first in Quick or Batch tab.")
    else:
        selected = st.multiselect(
            "Select files to search across",
            options=[h["filename"] for h in history],
            default=[history[0]["filename"]] if history else []
        )
        
        cross_keywords = st.text_input("Keywords (comma separated)", 
                                      placeholder="రామాయణం, کتاب, సీత")
        
        if st.button("Search Selected Files") and selected and cross_keywords.strip():
            results_all = []
            keywords = [k.strip() for k in cross_keywords.split(",") if k.strip()]
            
            with st.status("Searching across selected files...", expanded=True) as status:
                progress = st.progress(0)
                for i, fname in enumerate(selected):
                    try:
                        status.update(label=f"Processing {fname} ({i+1}/{len(selected)})", state="running")
                        path = UPLOAD_FOLDER / fname
                        if not path.exists():
                            st.warning(f"File {fname} not found in uploads folder.")
                            continue
                            
                        pages, src = processor.process_pdf(str(path))
                        if len(pages) == 0:
                            st.warning(f"No content extracted from {fname}")
                            continue
                            
                        res = engine.search_keywords(pages, keywords, src, fname)
                        results_all.extend(res)
                        
                    except Exception as e:
                        st.error(f"Error processing {fname}: {str(e)}")
                    
                    progress.progress((i + 1) / len(selected))
                
                status.update(label="Search complete", state="complete")
                
                if results_all:
                    df = pd.DataFrame([{
                        "File": r["filename"],
                        "Page": r["page"],
                        "Keyword": r["keyword"],
                        "Match": r["match"],
                        "Type": r["match_type"],
                        "Score": f"{r['score']:.1f}",
                        "Context": r["context"]
                    } for r in results_all])
                    
                    st.success(f"Found **{len(results_all)}** matches across **{len(selected)}** files")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No matches found in selected files. Try different keywords or check file content.")

# ─── HISTORY TAB ───────────────────────────────────────────────────────────
with tab_history:
    st.subheader("Processing History")
    if history:
        st.dataframe(pd.DataFrame(history))
    else:
        st.info("No files processed yet.")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")