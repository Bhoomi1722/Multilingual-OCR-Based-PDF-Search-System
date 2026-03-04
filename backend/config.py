from pathlib import Path
import os

BASE_DIR = Path(__file__).parent.parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILE_SIZE_MB = 50
MAX_PAGES_LIMIT = 20  # new: safeguard for large PDFs
TEXT_BASED_THRESHOLD_CHARS = 150
OCR_LANG = "tel+urd"
OCR_PREFERRED_PSMS = [6, 3, 4, 11, 12]
OCR_MIN_CONFIDENCE = 60
FUZZY_MATCH_THRESHOLD = 84

LOG_LEVEL = "INFO"