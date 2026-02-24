import fitz  # PyMuPDF
from pdf2image import convert_from_path
from typing import List, Tuple

from backend.config import TEXT_BASED_THRESHOLD_CHARS
from backend.utils import logger
from backend.ocr_handler import OCRHandler

class PDFProcessor:
    def __init__(self):
        self.ocr_handler = OCRHandler()

    def is_text_based(self, pdf_path: str) -> bool:
        try:
            doc = fitz.open(pdf_path)
            total_text = "".join(page.get_text() for page in doc)
            page_count = len(doc)
            doc.close()
            avg_chars = len(total_text.strip()) / max(1, page_count)
            logger.info(f"Detected avg chars per page: {avg_chars:.1f}")
            return avg_chars > TEXT_BASED_THRESHOLD_CHARS
        except Exception as e:
            logger.error(f"Text detection failed: {e}")
            return False

    def extract_unicode_text(self, pdf_path: str) -> List[Tuple[int, str, float]]:
        doc = fitz.open(pdf_path)
        pages = [(i+1, page.get_text("text").strip(), 100.0) for i, page in enumerate(doc)]
        doc.close()
        return pages

    def process_scanned_pdf(self, pdf_path: str) -> List[Tuple[int, str, float]]:
        images = convert_from_path(pdf_path, dpi=300)
        pages = []
        for idx, img in enumerate(images):
            logger.info(f"OCR page {idx+1}/{len(images)}")
            text, conf = self.ocr_handler.perform_ocr(img)
            pages.append((idx+1, text, conf))
        return pages

    def process_pdf(self, pdf_path: str) -> Tuple[List[Tuple[int, str, float]], str]:
        if self.is_text_based(pdf_path):
            return self.extract_unicode_text(pdf_path), "unicode"
        else:
            return self.process_scanned_pdf(pdf_path), "ocr"