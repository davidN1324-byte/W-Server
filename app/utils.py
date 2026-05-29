import os
import uuid
import json
import filetype
import unicodedata
import re
import hashlib
from pathlib import Path
from datetime import datetime
from fastapi import HTTPException
from app.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, ALLOWED_MIMES
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

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
    kind = filetype.guess(file_bytes)
    if kind:
        return kind.mime
    try:
        file_bytes.decode("utf-8")
        return "text/plain"
    except UnicodeDecodeError:
        return "application/octet-stream"


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def format_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


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
    result = []
    for stored, value in meta.items():
        file_path = UPLOAD_FOLDER / stored
        if not file_path.exists():
            continue
        if isinstance(value, dict):
            original = value.get("original", stored)
            size = value.get("size", file_path.stat().st_size)
            uploaded_at = value.get("uploaded_at", "")
        else:
            original = value
            size = file_path.stat().st_size
            uploaded_at = ""
        result.append({
            "stored": stored,
            "original": original,
            "size": format_size(size),
            "uploaded_at": uploaded_at,
        })
    return result

# ── Encryption ──

def _get_aes_key() -> bytes:
    from app.config import ENCRYPTION_KEY
    if ENCRYPTION_KEY:
        return base64.urlsafe_b64decode(ENCRYPTION_KEY)
    raise RuntimeError("ENCRYPTION_KEY not set in .env")


def encrypt_file(data: bytes) -> bytes:
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext


def decrypt_file(data: bytes) -> bytes:
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    nonce = data[:12]
    ciphertext = data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)