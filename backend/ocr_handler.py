import cv2
import numpy as np
import pytesseract
from PIL import Image
from typing import List, Tuple
from backend.config import OCR_LANG, OCR_PREPROCESS_DENOISE_KERNEL, OCR_PREFERRED_PSMS
from backend.utils import logger

class OCRHandler:
    def preprocess_image(self, pil_image) -> np.ndarray:
        img = np.array(pil_image.convert("RGB"))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Stronger denoising + contrast
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        gray = cv2.medianBlur(gray, OCR_PREPROCESS_DENOISE_KERNEL)
        
        # Deskew attempt (simple rotation correction)
        coords = np.column_stack(np.where(gray < 128))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = gray.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        gray = cv2.resize(gray, None, fx=1.8, fy=1.8, interpolation=cv2.INTER_CUBIC)
        kernel = np.ones((1, 1), np.uint8)
        gray = cv2.dilate(gray, kernel, iterations=1)
        gray = cv2.erode(gray, kernel, iterations=1)
        
        return gray

    def perform_ocr(self, image, lang: str = OCR_LANG) -> Tuple[str, float]:
        """Returns (text, average confidence)"""
        try:
            preprocessed = self.preprocess_image(image)
            
            best_text = ""
            best_conf = 0.0
            best_psm = 6

            for psm in OCR_PREFERRED_PSMS:
                config = f'--psm {psm} --oem 1 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789అఆఇఈఉఊఋఌఎఏఐఒఓఔకఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరఱలళవశషసహఽాిీుూృౄెేైొోౌ్ంఃఁఽ'
                data = pytesseract.image_to_data(
                    preprocessed, lang=lang, config=config, output_type=pytesseract.Output.DICT
                )
                
                text = " ".join(data["text"])
                confs = [int(c) for c in data["conf"] if int(c) >= 0]
                avg_conf = sum(confs) / len(confs) if confs else 0
                
                if avg_conf > best_conf:
                    best_conf = avg_conf
                    best_text = text
                    best_psm = psm

            logger.info(f"Best PSM: {best_psm}, Avg conf: {best_conf:.1f}%")
            return best_text.strip(), best_conf
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return "", 0.0

    def ocr_pdf_pages(self, images, lang: str = OCR_LANG) -> List[Tuple[int, str, float]]:
        pages = []
        for idx, img in enumerate(images):
            logger.info(f"OCR page {idx+1}/{len(images)}")
            text, conf = self.perform_ocr(img, lang)
            pages.append((idx + 1, text, conf))
        return pages