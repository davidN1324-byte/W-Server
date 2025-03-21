from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil
import logging
from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from utils import check_permissions, allowed_file, get_unique_filename, get_mime_type

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    files = [f.name for f in UPLOAD_FOLDER.iterdir() if f.is_file()]
    return templates.TemplateResponse("index.html", {"request": request, "files": files})

@router.get("/files")
async def list_files():
    files = [f.name for f in UPLOAD_FOLDER.iterdir() if f.is_file()]
    return {"files": files}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_bytes = await file.read()
    file_size = len(file_bytes)

    if file_size > MAX_CONTENT_LENGTH:
        raise HTTPException(status_code=413, detail="File too large")

    detected_mime = get_mime_type(file_bytes)
    if not allowed_file(file.filename, detected_mime):
        raise HTTPException(status_code=400, detail="Invalid file type")

    file.file.seek(0)  # Reset pointer after reading
    unique_filename = get_unique_filename(file.filename)
    file_path = UPLOAD_FOLDER / unique_filename

    if file_path.exists():
        raise HTTPException(status_code=409, detail="File already exists")

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": unique_filename, "message": "File uploaded successfully"}

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = UPLOAD_FOLDER / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="application/octet-stream", filename=filename)

@router.delete("/delete/{filename}")
async def delete_file(filename: str):
    file_path = UPLOAD_FOLDER / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path.unlink()
    return {"filename": filename, "message": "File deleted successfully"}