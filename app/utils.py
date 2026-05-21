import os
import hashlib
import magic
from pathlib import Path
from fastapi import HTTPException
from app.config import UPLOAD_FOLDER
from app.config import ALLOWED_EXTENSIONS, ALLOWED_MIMES
import uuid

def check_permissions(path: Path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    if not os.access(path, os.W_OK):
        raise HTTPException(status_code=500, detail=f"Permission denied to write to {path}")

def allowed_file(filename: str, content_type: str) -> bool:
    return filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS and content_type in ALLOWED_MIMES

def get_unique_filename(file_name: str) -> str:
    return f"{uuid.uuid4().hex}{Path(file_name).suffix}"

def get_mime_type(file_bytes: bytes) -> str:
    mime = magic.Magic(mime=True)
    return mime.from_buffer(file_bytes)

def get_file_list() -> list[str]:
    return [f.name for f in UPLOAD_FOLDER.iterdir() if f.is_file()]