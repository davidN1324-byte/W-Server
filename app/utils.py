import os
import hashlib
import magic
from pathlib import Path
from fastapi import HTTPException
from config import UPLOAD_FOLDER

def check_permissions(path: Path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    if not os.access(path, os.W_OK):
        raise HTTPException(status_code=500, detail=f"Permission denied to write to {path}")

def allowed_file(filename: str, content_type: str) -> bool:
    from config import ALLOWED_EXTENSIONS, ALLOWED_MIMES
    return filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS and content_type in ALLOWED_MIMES

def get_unique_filename(file_name: str) -> str:
    file_hash = hashlib.sha256(file_name.encode()).hexdigest()
    return file_hash + Path(file_name).suffix

def get_mime_type(file_bytes: bytes) -> str:
    mime = magic.Magic(mime=True)
    return mime.from_buffer(file_bytes)