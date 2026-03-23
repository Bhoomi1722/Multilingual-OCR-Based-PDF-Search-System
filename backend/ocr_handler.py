import cv2
import numpy as np
import pytesseract
from PIL import Image
from typing import Tuple
import easyocr

from backend.config import OCR_LANG, OCR_PREFERRED_PSMS
from backend.utils import logger

class OCRHandler:
    # Class-level (shared across all instances)
    _easy_reader = None
    _easy_reader_initialized = False

    def __init__(self):
        # Lazy initialize EasyOCR only once
        if not OCRHandler._easy_reader_initialized:
            try:
                logger.info("Initializing EasyOCR for Urdu support (one-time)")
                OCRHandler._easy_reader = easyocr.Reader(
                    ['ur', 'en'],
                    gpu=False,
                    verbose=False,
                    download_enabled=True
                )
                OCRHandler._easy_reader_initialized = True
                logger.info("EasyOCR initialized successfully")
            except Exception as e:
                logger.warning(f"EasyOCR initialization failed: {e}. "
                               "Urdu fallback will be disabled. "
                               "You can retry later or delete ~/.EasyOCR/model/ to force redownload.")
                OCRHandler._easy_reader = None
                OCRHandler._easy_reader_initialized = True  # prevent retry spam

    @property
    def easy_reader(self):
        return OCRHandler._easy_reader

    def preprocess_image(self, pil_image) -> np.ndarray:
        img = np.array(pil_image.convert("RGB"))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        gray = cv2.medianBlur(gray, 3)
        
        # Deskew
        coords = np.column_stack(np.where(gray < 128))
        if len(coords) == 0:
            return gray
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle += 90
        (h, w) = gray.shape
        M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
        gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        gray = cv2.resize(gray, None, fx=1.8, fy=1.8, interpolation=cv2.INTER_CUBIC)
        kernel = np.ones((1,1), np.uint8)
        gray = cv2.dilate(gray, kernel, iterations=1)
        gray = cv2.erode(gray, kernel, iterations=1)
        
        return gray

    def perform_ocr(self, image, lang: str = OCR_LANG) -> Tuple[str, float]:
        try:
            preprocessed = self.preprocess_image(image)
            best_text = ""
            best_conf = 0.0
            best_psm = 6

            # Tesseract (primary for Telugu + Urdu)
            for psm in OCR_PREFERRED_PSMS:
                config = f'--psm {psm} --oem 1'
                data = pytesseract.image_to_data(
                    preprocessed, lang=lang, config=config, 
                    output_type=pytesseract.Output.DICT
                )
                text = " ".join(t for t in data["text"] if t.strip())
                confs = [int(c) for c in data["conf"] if int(c) >= 0]
                avg_conf = sum(confs) / len(confs) if confs else 0
                
                if avg_conf > best_conf:
                    best_conf = avg_conf
                    best_text = text
                    best_psm = psm

            logger.info(f"Best Tesseract PSM: {best_psm}, Avg conf: {best_conf:.1f}%")

            # EasyOCR fallback for Urdu (only if initialized)
            if self.easy_reader and ("urd" in lang.lower() or lang == "ur"):
                try:
                    results = self.easy_reader.readtext(np.array(image), detail=1, paragraph=True)
                    if results:
                        text_easy = " ".join(txt for _, txt, _ in results)
                        conf_easy = sum(conf for _, _, conf in results) * 100 / len(results)
                        if conf_easy > best_conf + 5:
                            logger.info(f"EasyOCR better for Urdu: {conf_easy:.1f}% vs Tesseract {best_conf:.1f}%")
                            return text_easy.strip(), conf_easy
                except Exception as e:
                    logger.warning(f"EasyOCR fallback failed: {e}")

            return best_text.strip(), best_conf

        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return "", 0.0