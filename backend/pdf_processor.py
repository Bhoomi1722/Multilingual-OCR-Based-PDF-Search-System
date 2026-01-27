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
            total_text = ""
            page_count = len(doc)
            for page in doc:
                total_text += page.get_text()
            doc.close()
            avg_chars = len(total_text.strip()) / max(1, page_count)
            logger.info(f"Detected avg chars per page: {avg_chars}")
            return avg_chars > TEXT_BASED_THRESHOLD_CHARS
        except Exception as e:
            logger.error(f"Text detection failed: {e}")
            return False

    def extract_unicode_text(self, pdf_path: str) -> List[Tuple[int, str]]:
        try:
            doc = fitz.open(pdf_path)
            pages_text = []
            for i, page in enumerate(doc):
                text = page.get_text("text")
                pages_text.append((i + 1, text))
            doc.close()
            logger.info(f"Extracted Unicode text from {len(pages_text)} pages")
            return pages_text
        except Exception as e:
            logger.error(f"Unicode extraction failed: {e}")
            raise

    def convert_to_images(self, pdf_path: str):
        try:
            images = convert_from_path(pdf_path, dpi=300)
            logger.info(f"Converted PDF to {len(images)} images")
            return images
        except Exception as e:
            logger.error(f"PDF to image conversion failed: {e}")
            raise

    def process_pdf(self, pdf_path: str) -> Tuple[List[Tuple[int, str]], str]:
        if self.is_text_based(pdf_path):
            pages_text = self.extract_unicode_text(pdf_path)
            source = "unicode"
        else:
            images = self.convert_to_images(pdf_path)
            pages_text = self.ocr_handler.ocr_pdf_pages(images)
            source = "ocr"
        return pages_text, source