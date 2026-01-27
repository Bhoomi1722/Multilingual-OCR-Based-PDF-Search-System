import streamlit as st
# ────────────────────────────────────────────────
# Force project root into sys.path (makes imports reliable)
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]          # go up one level from frontend/
sys.path.insert(0, str(PROJECT_ROOT))
# ────────────────────────────────────────────────

# Now normal imports work
from backend.pdf_processor import PDFProcessor
from backend.search_engine import SearchEngine
from backend.utils import save_uploaded_file, cleanup_temp_file, PDFProcessingError
# ... rest of your file ...
import time

st.set_page_config(page_title="Multilingual OCR PDF Search", layout="wide")
st.title("Multilingual OCR-Based PDF Search System")
st.markdown("**Telugu & Urdu keyword search in Unicode or scanned PDFs**")

with st.sidebar:
    st.header("Settings")
    st.info("Tesseract must have tel+urd languages installed")

uploaded_file = st.file_uploader("Upload PDF (Unicode or Scanned)", type="pdf")
keywords_input = st.text_input("Enter keywords (comma-separated, Telugu/Urdu supported)", placeholder="పుస్తకం, کتاب")
search_button = st.button("🔍 Search Document", type="primary")

if search_button and uploaded_file and keywords_input:
    with st.spinner("Processing PDF..."):
        try:
            filepath = save_uploaded_file(uploaded_file)
            processor = PDFProcessor()
            page_texts, source = processor.process_pdf(filepath)
            
            search_engine = SearchEngine()
            keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
            
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            results = search_engine.search_keywords(page_texts, keywords, source)
            cleanup_temp_file(filepath)
            
            if results:
                st.success(f"✅ Found {len(results)} matches")
                tab1, tab2 = st.tabs(["📋 Results Table", "📄 Raw Text Samples"])
                
                with tab1:
                    for res in results:
                        with st.expander(f"Page {res['page']} • {res['keyword']}"):
                            st.write(f"**Match:** {res['match']}")
                            st.write(f"**Source:** {res['source'].upper()}")
                            st.write(f"**Context:** {res['context']}")
                
                with tab2:
                    st.write("Sample extracted/OCR text (first 3 pages):")
                    for page_num, text in page_texts[:3]:
                        st.write(f"**Page {page_num}:**")
                        st.code(text[:500] + "..." if len(text) > 500 else text, language=None)
            else:
                st.warning("No matches found for the given keywords.")
        except PDFProcessingError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            st.info("Check logs or ensure Tesseract/Poppler are installed correctly.")
