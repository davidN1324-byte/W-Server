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

