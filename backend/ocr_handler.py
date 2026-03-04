import cv2
import numpy as np
import pytesseract
from PIL import Image
from typing import Tuple
import easyocr

from backend.config import OCR_LANG, OCR_PREFERRED_PSMS
from backend.utils import logger

class OCRHandler:
    def __init__(self):
        self.easy_reader = None
        try:
            self.easy_reader = easyocr.Reader(['ur', 'en'], gpu=False, verbose=False, download_enabled=True)
            logger.info("EasyOCR initialized for Urdu support")
        except Exception as e:
            logger.warning(f"EasyOCR failed to load: {e}. Urdu fallback disabled. You can retry later or delete ~/.EasyOCR/model/ to force redownload.")
            self.easy_reader = None

    def preprocess_image(self, pil_image) -> np.ndarray:
        img = np.array(pil_image.convert("RGB"))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        gray = cv2.medianBlur(gray, 3)
        
        coords = np.column_stack(np.where(gray < 128))
        if len(coords) == 0:
            return gray
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
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

            # Tesseract path (Telugu primary)
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

            # EasyOCR fallback for Urdu
            if self.easy_reader and ("urd" in lang.lower() or lang == "ur"):
                try:
                    results = self.easy_reader.readtext(np.array(image), detail=1, paragraph=True)
                    if results:
                        text_easy = " ".join(txt for _, txt, _ in results)
                        conf_easy = sum(conf for _, _, conf in results) / len(results) * 100
                        if conf_easy > best_conf + 5:  # prefer if noticeably better
                            logger.info(f"EasyOCR better for Urdu: {conf_easy:.1f}% vs Tesseract {best_conf:.1f}%")
                            return text_easy.strip(), conf_easy
                except Exception as e:
                    logger.warning(f"EasyOCR failed: {e}")

            logger.info(f"Best PSM: {best_psm}, Avg conf: {best_conf:.1f}%")
            return best_text.strip(), best_conf
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return "", 0.0