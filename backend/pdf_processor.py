import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
import json
from pathlib import Path
from typing import List, Tuple

from backend.config import (
    TEXT_BASED_THRESHOLD_CHARS, MAX_PAGES_LIMIT,
    CACHE_DIR, THUMBNAIL_DIR
)
from backend.utils import logger
from backend.ocr_handler import OCRHandler

class PDFProcessor:
    def __init__(self):
        self.ocr_handler = OCRHandler()

    def is_text_based(self, pdf_path: str) -> bool:
        """Check if PDF has enough extractable text (not scanned/image-only)"""
        try:
            doc = fitz.open(pdf_path)
            total_text = ""
            for page in doc:
                total_text += page.get_text("text") or ""
            page_count = len(doc)
            doc.close()
            avg_chars = len(total_text.strip()) / max(1, page_count)
            logger.info(f"PDF {Path(pdf_path).name}: avg chars/page = {avg_chars:.1f}")
            return avg_chars > TEXT_BASED_THRESHOLD_CHARS
        except Exception as e:
            logger.error(f"Text detection failed for {pdf_path}: {e}")
            return False

    def get_cache_path(self, pdf_path: str) -> Path:
        pdf_hash = str(hash(str(pdf_path)))
        return CACHE_DIR / f"{pdf_hash}.json"

    def load_from_cache(self, pdf_path: str) -> Tuple[List[Tuple[int, str, float]], str] | None:
        cache_file = self.get_cache_path(pdf_path)
        if cache_file.exists():
            try:
                with open(cache_file, encoding="utf-8") as f:
                    data = json.load(f)
                logger.info(f"Loaded from cache: {pdf_path}")
                return data["pages"], data["source"]
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")
        return None

    def save_to_cache(self, pdf_path: str, pages: List[Tuple[int, str, float]], source: str):
        cache_file = self.get_cache_path(pdf_path)
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump({"pages": pages, "source": source}, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved to cache: {pdf_path}")
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")

    def generate_thumbnail(self, pdf_path: str) -> str | None:
        try:
            images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=100)
            if images:
                thumb_path = THUMBNAIL_DIR / f"{Path(pdf_path).stem}.jpg"
                images[0].save(thumb_path, "JPEG")
                return str(thumb_path)
        except Exception as e:
            logger.warning(f"Thumbnail generation failed: {e}")
        return None

    def extract_unicode_text(self, pdf_path: str) -> List[Tuple[int, str, float]]:
        doc = fitz.open(pdf_path)
        pages = [(i+1, page.get_text("text").strip(), 100.0) for i, page in enumerate(doc)]
        doc.close()
        return pages

    def process_scanned_pdf(self, pdf_path: str) -> List[Tuple[int, str, float]]:
        images = convert_from_path(pdf_path, dpi=300)
        if len(images) > MAX_PAGES_LIMIT:
            logger.warning(f"Large scanned PDF → limiting to first {MAX_PAGES_LIMIT} pages")
            images = images[:MAX_PAGES_LIMIT]
        
        pages = []
        for idx, img in enumerate(images):
            logger.info(f"OCR page {idx+1}/{len(images)}")
            text, conf = self.ocr_handler.perform_ocr(img)
            pages.append((idx+1, text, conf))
        return pages

    def process_pdf(self, pdf_path: str) -> Tuple[List[Tuple[int, str, float]], str]:
        # Try cache first
        cached = self.load_from_cache(pdf_path)
        if cached:
            return cached

        filename = Path(pdf_path).name
        pages = []
        source_type = "unknown"

        try:
            if self.is_text_based(pdf_path):
                pages = self.extract_unicode_text(pdf_path)
                source_type = "unicode"
            else:
                pages = self.process_scanned_pdf(pdf_path)
                source_type = "ocr"

            self.save_to_cache(pdf_path, pages, source_type)
            return pages, source_type

        except Exception as e:
            logger.error(f"Full processing failed for {filename}: {e}")
            return [], "error"