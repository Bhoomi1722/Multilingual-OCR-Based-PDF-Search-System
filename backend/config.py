import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILE_SIZE_MB = 50
TEXT_BASED_THRESHOLD_CHARS = 150   # average chars per page to classify as Unicode
OCR_PREPROCESS_DENOISE_KERNEL = 3
OCR_LANG = "tel+urd"
TESSDATA_PREFIX = os.getenv("TESSDATA_PREFIX", "/usr/share/tesseract-ocr/5/tessdata")
LOG_LEVEL = "INFO"

# OCR improvements
OCR_PREFERRED_PSMS = [6, 3, 4, 11, 12]   # order of preference
OCR_MIN_CONFIDENCE = 60                   # warn if average below this
FUZZY_MATCH_THRESHOLD = 84                # rapidfuzz score %

# Report output path
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)