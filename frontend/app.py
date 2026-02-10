import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
from io import StringIO, BytesIO
from fpdf import FPDF
import re
import time

from backend.pdf_processor import PDFProcessor
from backend.search_engine import SearchEngine
from backend.utils import (
    save_uploaded_file, cleanup_temp_file, PDFProcessingError,
    init_db, save_processed, get_processed_files
)

init_db()

if "pdf_buffer" not in st.session_state:
    st.session_state.pdf_buffer = None
if "pdf_filename" not in st.session_state:
    st.session_state.pdf_filename = None

st.set_page_config(page_title="Multilingual OCR PDF Search", layout="wide")
st.title("Multilingual OCR-Based PDF Search System")
st.markdown("**Telugu & Urdu – Improved OCR & Fuzzy Search**  •  ~60–70% Prototype")

with st.sidebar:
    st.header("Settings")
    st.info("Tesseract must have tel+urd languages installed")

tab_search, tab_history = st.tabs(["📤 Search PDF", "📚 History"])

with tab_search:
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    keywords_input = st.text_input(
        "Keywords (comma separated, Telugu/Urdu supported)",
        placeholder="పుస్తకం, రాముడు, کتاب"
    )
    search_btn = st.button("🔍 Search", type="primary", use_container_width=True)

    if search_btn and uploaded_file and keywords_input:
        with st.spinner("Processing (improved OCR + fuzzy search)..."):
            try:
                filepath = save_uploaded_file(uploaded_file)
                processor = PDFProcessor()
                page_data, source = processor.process_pdf(filepath)   # now returns list of (page, text, conf)

                full_text_all = " ".join(item[1] for item in page_data)  # safe: take second element
                save_processed(uploaded_file.name, len(page_data), source, len(full_text_all))

                keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]

                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.008)
                    progress.progress(i + 1)

                engine = SearchEngine()
                results = engine.search_keywords(page_data, keywords, source)

                cleanup_temp_file(filepath)
                progress.empty()

                if results:
                    st.success(f"Found {len(results)} matches (exact + fuzzy)")

                    # ─── Results with context highlights ────────────────────────────────
                    st.subheader("Search Results (context snippets)")
                    for res in results:
                        with st.expander(f"Page {res['page']} • {res['keyword']}  ({res['match_type'].upper()})"):
                            st.write(f"**Matched:** {res['match']}")
                            highlighted = res['context'].replace(
                                res['match'],
                                f"<mark style='background:#ffff99; padding:2px 4px'>{res['match']}</mark>"
                            )
                            st.markdown(f"**Context:** {highlighted}", unsafe_allow_html=True)
                            st.caption(f"Confidence: {res['page_conf']:.1f}% • {res['source'].upper()}")

                    # ─── Full page view with all highlights ─────────────────────────────
                    st.subheader("Full Page Text – All Matches Highlighted")
                    for page_num, text, conf in page_data:
                        highlighted_text = text
                        for res in [r for r in results if r["page"] == page_num]:
                            pattern = re.escape(res["match"])
                            highlighted_text = re.sub(
                                f"({pattern})",
                                r"<mark style='background:#ffff99; padding:2px 4px'>\1</mark>",
                                highlighted_text,
                                flags=re.IGNORECASE
                            )
                        with st.expander(f"Page {page_num} (conf: {conf:.1f}%)"):
                            st.markdown(highlighted_text, unsafe_allow_html=True)

                    # ─── CSV export ─────────────────────────────────────────────────────
                    df = pd.DataFrame([
                        {
                            "Page": r["page"],
                            "Keyword": r["keyword"],
                            "Match": r["match"],
                            "Match Type": r["match_type"],
                            "Context": r["context"],
                            "Confidence": f"{r['page_conf']:.1f}%",
                            "Source": r["source"]
                        } for r in results
                    ])

                    # ─── Put this AFTER the if results: block, but still indented under if results: ───
                    st.subheader("Export Options")
                    col1, col2 = st.columns(2)

                    with col1:
                        # CSV button (already working)
                        csv_buffer = StringIO()
                        df.to_csv(csv_buffer, index=False)
                        st.download_button(
                            "Download Results CSV",
                            csv_buffer.getvalue(),
                            f"{uploaded_file.name}_results.csv",
                            "text/csv",
                            key="csv_download"
                        )

                    # Generate PDF only once when results are ready
                    if results and st.session_state.pdf_buffer is None:
                        with st.spinner("Preparing PDF report (using ReportLab)..."):
                            try:
                                from reportlab.lib.pagesizes import letter
                                from reportlab.pdfgen import canvas
                                from reportlab.pdfbase import pdfmetrics
                                from reportlab.pdfbase.ttfonts import TTFont
                                from io import BytesIO

                                pdf_buffer = BytesIO()
                                c = canvas.Canvas(pdf_buffer, pagesize=letter)
                                width, height = letter

                                # Register fonts (absolute path)
                                font_path_tel = str(Path(__file__).parent.parent / "AnekTelugu-Regular.ttf")
                                font_path_urd = str(Path(__file__).parent.parent / "NotoNastaliqUrdu-Regular.ttf")

                                pdfmetrics.registerFont(TTFont('NotoTelugu', font_path_tel))
                                pdfmetrics.registerFont(TTFont('NotoUrdu', font_path_urd))

                                # Choose font
                                font_family = 'NotoTelugu'  # default
                                if any(c in 'اردو کتاب رام' for c in full_text_all[:200]):
                                    font_family = 'NotoUrdu'

                                c.setFont(font_family, 14)

                                # Title
                                c.drawCentredString(width/2, height - 50, f"Search Report: {uploaded_file.name}")
                                c.drawCentredString(width/2, height - 70, f"Keywords: {', '.join(keywords)}")
                                y = height - 100

                                c.setFont(font_family, 12)
                                c.drawString(50, y, "Extracted Content with Matches")
                                y -= 30

                                # Content per page
                                for page_num, text, conf in page_data[:10]:  # limit pages
                                    c.setFont(font_family, 12)
                                    c.drawString(50, y, f"Page {page_num} (conf: {conf:.1f}%)")
                                    y -= 20

                                    c.setFont(font_family, 10)

                                    page_text = text[:2000]
                                    # Replace matches with visible markers
                                    for res in [r for r in results if r["page"] == page_num]:
                                        page_text = page_text.replace(res["match"], f"[{res['match']}]")

                                    # Split text into lines (ReportLab doesn't auto-wrap well)
                                    lines = page_text.split('\n')
                                    for line in lines:
                                        if y < 50:  # new page if needed
                                            c.showPage()
                                            y = height - 50
                                            c.setFont(font_family, 10)
                                        c.drawString(50, y, line)
                                        y -= 12

                                    y -= 20  # space between pages

                                c.save()
                                pdf_buffer.seek(0)

                                st.session_state.pdf_buffer = pdf_buffer
                                st.session_state.pdf_filename = f"{uploaded_file.name}_report.pdf"

                                st.success("PDF report ready using ReportLab! Download below.")

                            except Exception as e:
                                st.error(f"PDF failed: {str(e)}")
                                st.info("Common fixes:\n1. Ensure .ttf files are in project root\n2. Check filenames exactly match\n3. pip install reportlab\n4. Try smaller text limits if PDF is too big")

                    # ─── Download button ──────────────────────────────────────────────────────────
                    if st.session_state.pdf_buffer is not None:
                        st.download_button(
                            label="Download PDF Report (with highlights)",
                            data=st.session_state.pdf_buffer,
                            file_name=st.session_state.pdf_filename,
                            mime="application/pdf",
                            key="pdf_download_final"
                        )
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Check terminal / ensure Tesseract + tel+urd traineddata installed")

with tab_history:
    st.subheader("Processed Files History")
    history = get_processed_files()
    if history:
        st.dataframe(pd.DataFrame(history))
    else:
        st.info("No files processed yet.")