import os
import uuid
import json
import magic
import unicodedata
import re
from pathlib import Path
from fastapi import HTTPException
from app.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, ALLOWED_MIMES

METADATA_FILE = UPLOAD_FOLDER / "metadata.json"


def check_permissions(path: Path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    if not os.access(path, os.W_OK):
        raise HTTPException(status_code=500, detail=f"Permission denied to write to {path}")


def allowed_file(filename: str, content_type: str) -> bool:
    return filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS and content_type in ALLOWED_MIMES


def sanitize_filename(filename: str) -> str:
    filename = unicodedata.normalize("NFC", filename)
    filename = re.sub(r'[^\w\s\-.]', '_', filename)
    filename = filename.strip()
    return filename or "file"


def get_unique_filename(original_name: str) -> str:
    ext = Path(original_name).suffix.lower()
    return f"{uuid.uuid4().hex}{ext}"


def get_mime_type(file_bytes: bytes) -> str:
    mime = magic.Magic(mime=True)
    return mime.from_buffer(file_bytes)


def load_metadata() -> dict:
    if METADATA_FILE.exists():
        with METADATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_metadata(data: dict):
    with METADATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_file_list() -> list[dict]:
    meta = load_metadata()
    return [
        {"stored": stored, "original": original}
        for stored, original in meta.items()
        if (UPLOAD_FOLDER / stored).exists()
    ]