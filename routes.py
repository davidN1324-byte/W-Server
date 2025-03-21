from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil
import logging
from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from utils import check_permissions, allowed_file, get_unique_filename, get_mime_type

