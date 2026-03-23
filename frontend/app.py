import streamlit as st
import pandas as pd
import re
import os
import time
from pathlib import Path
from datetime import datetime
from io import BytesIO
from PIL import Image

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

from backend.config import (
    MAX_FILE_SIZE_MB, TEXT_BASED_THRESHOLD_CHARS, MAX_PAGES_LIMIT,
    OCR_LANG, OCR_PREFERRED_PSMS, FUZZY_MATCH_THRESHOLD, UPLOAD_FOLDER,
    REPORT_DIR, THUMBNAIL_DIR
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
st.caption("Telugu + Urdu • Scanned & Digital PDFs • Exact + Fuzzy Matching • 100% Complete")

processor = PDFProcessor()
engine = SearchEngine()

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
        show_thumbnails = st.checkbox("Show thumbnails", value=True)
        show_full_pages = st.checkbox("Show full page previews", value=False)
        highlight_color = st.color_picker("Highlight color", "#ffff99")
        max_results_show = st.slider("Max results to expand", 3, 20, 8)
    
    with st.expander("About", expanded=False):
        st.caption("Final Year Project – Multilingual OCR-Based PDF Search")
        st.caption("Telugu: Stable & production-ready")
        st.caption("Urdu: Basic but functional (EasyOCR fallback)")
        st.caption("Status: 100% complete – ready for submission")

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
    "📊 History & Reports"
])

# ─── QUICK SEARCH ──────────────────────────────────────────────────────────
with tab_quick:
    st.subheader("Single Document Search")
    
    c1, c2 = st.columns([5, 3])
    with c1:
        uploaded_file = st.file_uploader("Upload PDF", type="pdf", key="quick_uploader")
    with c2:
        keywords_input = st.text_input("Keywords (comma separated)", 
                                      placeholder="రామాయణం, کتاب, పుస్తకం",
                                      key="quick_keywords")

    if st.button("🔍 Search", type="primary", key="quick_search") and uploaded_file and keywords_input.strip():
        with st.status("Processing PDF...", expanded=True) as status:
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
                    
                    # Thumbnail
                    if show_thumbnails:
                        thumb_path = processor.generate_thumbnail(filepath)
                        if thumb_path:
                            st.image(thumb_path, caption="First Page Thumbnail", width=300)
                    
                    # Results cards
                    for i, r in enumerate(results[:max_results_show]):
                        with st.expander(f"Page {r['page']} • {r['keyword']} • {r['match_type']} • score {r['score']:.0f}"):
                            st.markdown(f"**Match:** {r['match']}")
                            st.markdown(r['context'])
                            st.caption(f"conf {r['page_conf']:.1f}%")
                    
                    # Full page highlights
                    if show_full_pages:
                        with st.expander("Full Pages Highlights"):
                            for page_num, text, conf in page_data[:8]:
                                h_text = text
                                for r in [r for r in results if r["page"] == page_num]:
                                    h_text = re.sub(
                                        f"({re.escape(r['match'])})",
                                        f"<mark style='background:{highlight_color}; padding:2px; border-radius:3px;'>\\1</mark>",
                                        h_text, flags=re.I
                                    )
                                st.markdown(f"**Page {page_num}** (conf {conf:.1f}%)  \n{h_text}", unsafe_allow_html=True)
                
                # PDF Report Button (now visible after search)
                if st.button("Generate & Download PDF Report", key="quick_pdf_report"):
                    pdf_buffer = BytesIO()
                    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
                    styles = getSampleStyleSheet()
                    story = []
                    story.append(Paragraph(f"Search Report: {uploaded_file.name}", styles['Title']))
                    story.append(Spacer(1, 12))
                    story.append(Paragraph(f"Keywords: {keywords_input}", styles['Normal']))
                    story.append(Spacer(1, 12))
                    story.append(Paragraph(f"Source: {source.upper()} • Pages: {len(page_data)}", styles['Normal']))
                    story.append(Spacer(1, 24))
                    
                    for r in results:
                        story.append(Paragraph(f"Page {r['page']} - {r['keyword']} ({r['match_type']}, score {r['score']:.1f})", styles['Heading2']))
                        story.append(Paragraph(r['context'], styles['Normal']))
                        story.append(Spacer(1, 12))
                    
                    doc.build(story)
                    pdf_buffer.seek(0)
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"OCR_Search_Report_{uploaded_file.name}.pdf",
                        mime="application/pdf",
                        key="quick_download_pdf"
                    )
                
            except Exception as e:
                status.update(label=f"Error: {str(e)}", state="error")

# ─── BATCH UPLOAD ──────────────────────────────────────────────────────────
with tab_batch:
    st.subheader("Batch / Multi-file Upload & Search")
    
    uploaded_files = st.file_uploader("Upload multiple PDFs", type="pdf", accept_multiple_files=True, key="batch_uploader")
    batch_keywords = st.text_input("Keywords (comma separated)", key="batch_keywords")
    
    if st.button("Search All Files", type="primary", key="batch_search") and uploaded_files and batch_keywords.strip():
        all_results = []
        keywords = [k.strip() for k in batch_keywords.split(",") if k.strip()]
        
        progress = st.progress(0)
        status_text = st.empty()
        
        for i, file in enumerate(uploaded_files):
            status_text.text(f"Processing {file.name} ({i+1}/{len(uploaded_files)})...")
            try:
                path = save_uploaded_file(file)
                pages, src = processor.process_pdf(path)
                if len(pages) > MAX_PAGES_LIMIT:
                    pages = pages[:MAX_PAGES_LIMIT]
                full = " ".join(t for _, t, _ in pages)
                save_processed(file.name, len(pages), src, len(full))
                
                res = engine.search_keywords(pages, keywords, src, file.name)
                all_results.extend(res)
            except Exception as e:
                st.warning(f"Skipped {file.name}: {e}")
            progress.progress((i+1)/len(uploaded_files))
        
        status_text.text("Batch processing complete")
        
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
            st.success(f"Found {len(all_results)} matches across {len(uploaded_files)} files")

            # PDF Report for Batch
            if st.button("Generate & Download PDF Report (Batch)", key="batch_pdf_report"):
                pdf_buffer = BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []
                story.append(Paragraph("Batch Search Report", styles['Title']))
                story.append(Spacer(1, 12))
                story.append(Paragraph(f"Keywords: {batch_keywords}", styles['Normal']))
                story.append(Spacer(1, 12))
                story.append(Paragraph(f"Files processed: {len(uploaded_files)}", styles['Normal']))
                story.append(Spacer(1, 24))
                
                for r in all_results:
                    story.append(Paragraph(f"{r['filename']} - Page {r['page']} - {r['keyword']} ({r['match_type']})", styles['Heading2']))
                    story.append(Paragraph(r['context'], styles['Normal']))
                    story.append(Spacer(1, 12))
                
                doc.build(story)
                pdf_buffer.seek(0)
                st.download_button(
                    label="Download Batch PDF Report",
                    data=pdf_buffer,
                    file_name="OCR_Batch_Report.pdf",
                    mime="application/pdf",
                    key="batch_download_pdf"
                )

# ─── CROSS-FILE SEARCH ─────────────────────────────────────────────────────
with tab_cross:
    st.subheader("Cross-File Search (From History)")
    
    history = get_processed_files()
    if not history:
        st.info("No processed files yet. Upload some PDFs first.")
    else:
        selected_files = st.multiselect(
            "Select files to search across",
            options=[h["filename"] for h in history],
            default=[history[0]["filename"]] if history else [],
            key="cross_select"
        )
        
        cross_keywords = st.text_input("Keywords (comma separated)", 
                                      placeholder="రామాయణం, کتاب, పుస్తకం",
                                      key="cross_keywords")
        
        if st.button("Search Across Selected Files", type="primary", key="cross_search") and selected_files and cross_keywords.strip():
            all_results = []
            keywords = [k.strip() for k in cross_keywords.split(",") if k.strip()]
            
            progress = st.progress(0)
            status_text = st.empty()
            
            for i, fname in enumerate(selected_files):
                status_text.text(f"Searching {fname} ({i+1}/{len(selected_files)})...")
                try:
                    path = UPLOAD_FOLDER / fname
                    if not path.exists():
                        st.warning(f"File {fname} not found")
                        continue
                        
                    pages, src = processor.process_pdf(str(path))
                    res = engine.search_keywords(pages, keywords, src, fname)
                    all_results.extend(res)
                except Exception as e:
                    st.warning(f"Error in {fname}: {e}")
                progress.progress((i+1)/len(selected_files))
            
            status_text.text("Cross-file search complete")
            
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
                st.success(f"Found {len(all_results)} matches across {len(selected_files)} files")
            else:
                st.info("No matches found. Try different keywords.")

# ─── HISTORY TAB ───────────────────────────────────────────────────────────
with tab_history:
    st.subheader("Processing History")
    if history:
        df_hist = pd.DataFrame(history)
        st.dataframe(df_hist)
        
        selected_hist = st.selectbox("Preview file", df_hist["filename"], key="hist_preview")
        if selected_hist:
            thumb_path = THUMBNAIL_DIR / f"{Path(selected_hist).stem}.jpg"
            if thumb_path.exists():
                st.image(str(thumb_path), caption=f"First page of {selected_hist}", width=400)
            else:
                st.info("No thumbnail available")
    else:
        st.info("No files processed yet.")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")