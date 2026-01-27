import os
import logging
from pathlib import Path
from typing import List, Tuple
from backend.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFProcessingError(Exception):
    pass

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(uploaded_file) -> str:
    if not allowed_file(uploaded_file.name):
        raise PDFProcessingError("Invalid file type. Only PDF allowed.")
    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise PDFProcessingError(f"File too large. Max {MAX_FILE_SIZE_MB}MB.")
    filepath = UPLOAD_FOLDER / uploaded_file.name
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    logger.info(f"Saved file: {filepath}")
    return str(filepath)

def cleanup_temp_file(filepath: str):
    try:
        os.remove(filepath)
        logger.info(f"Cleaned up: {filepath}")
    except Exception as e:
        logger.warning(f"Cleanup failed: {e}")

def get_context(text: str, word: str, window: int = 60) -> str:
    pos = text.find(word)
    if pos == -1:
        return ""
    start = max(0, pos - window)
    end = min(len(text), pos + len(word) + window)
    return "..." + text[start:end] + "..."