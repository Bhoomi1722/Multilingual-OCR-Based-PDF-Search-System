import logging
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any
import sqlite3
from datetime import datetime
from backend.config import BASE_DIR,MAX_FILE_SIZE_MB,UPLOAD_FOLDER

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFProcessingError(Exception):
    pass

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {"pdf"}

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

def get_context(text: str, word: str, window: int = 80) -> str:
    pos = text.lower().find(word.lower())
    if pos == -1:
        return ""
    start = max(0, pos - window)
    end = min(len(text), pos + len(word) + window)
    return "..." + text[start:end] + "..."

# ─── SQLite helpers ────────────────────────────────────────────────────────────

DB_PATH = BASE_DIR / "data" / "processed.db"

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS processed_files (
            filename TEXT PRIMARY KEY,
            processed_at TEXT,
            page_count INTEGER,
            source_type TEXT,
            text_length INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_processed(filename: str, page_count: int, source: str, text_length: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''
        INSERT OR REPLACE INTO processed_files 
        (filename, processed_at, page_count, source_type, text_length)
        VALUES (?, ?, ?, ?, ?)
    ''', (filename, now, page_count, source, text_length))
    conn.commit()
    conn.close()

def get_processed_files() -> list:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT filename, processed_at, source_type, page_count FROM processed_files ORDER BY processed_at DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    return [{"filename": r[0], "date": r[1], "source": r[2], "pages": r[3]} for r in rows]