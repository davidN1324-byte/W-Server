from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from utils import check_permissions, allowed_file, get_unique_filename
import os
import shutil
import logging
import hashlib
import magic
from pathlib import Path

UPLOAD_FOLDER = Path(__file__).parent / "uploads"
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}
ALLOWED_MIMES = {"text/plain", "application/pdf", "image/png", "image/jpeg", "image/gif"}

