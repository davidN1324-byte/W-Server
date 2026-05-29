from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging
from app.config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from app.utils import (
    allowed_file, get_unique_filename, get_mime_type, get_file_list,
    sanitize_filename, load_metadata, save_metadata, compute_sha256,
    encrypt_file, decrypt_file
)
from app.auth import verify_token

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"files": get_file_list()})


@router.get("/files", dependencies=[Depends(verify_token)])
@limiter.limit("30/minute")
async def list_files(request: Request):
    return {"files": get_file_list()}


@router.post("/upload", dependencies=[Depends(verify_token)])
@limiter.limit("10/minute")
async def upload_file(request: Request, file: UploadFile = File(...)):
    file_bytes = await file.read()

    if len(file_bytes) > MAX_CONTENT_LENGTH:
        raise HTTPException(status_code=413, detail="File too large")

    detected_mime = get_mime_type(file_bytes)
    if not allowed_file(file.filename, detected_mime):
        raise HTTPException(status_code=400, detail="Invalid file type")

    original_name = sanitize_filename(file.filename)
    stored_name = get_unique_filename(original_name)
    file_path = UPLOAD_FOLDER / stored_name

    encrypted = encrypt_file(file_bytes)
    with file_path.open("wb") as buffer:
        buffer.write(encrypted)

    meta = load_metadata()
    meta[stored_name] = {
        "original": original_name,
        "sha256": compute_sha256(file_bytes),
        "size": len(file_bytes),
        "uploaded_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
        "encrypted": True,
    }
    save_metadata(meta)

    logger.info("Uploaded: %s → %s", original_name, stored_name)
    return {"filename": stored_name, "original": original_name, "message": "File uploaded successfully"}


@router.get("/download/{filename}", dependencies=[Depends(verify_token)])
async def download_file(request: Request, filename: str):
    file_path = UPLOAD_FOLDER / filename
    if not file_path.resolve().is_relative_to(UPLOAD_FOLDER.resolve()):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    meta = load_metadata()
    entry = meta.get(filename, {})
    original_name = entry.get("original", filename) if isinstance(entry, dict) else entry
    is_encrypted = entry.get("encrypted", False) if isinstance(entry, dict) else False

    encrypted_data = file_path.read_bytes()

    if is_encrypted:
        try:
            file_data = decrypt_file(encrypted_data)
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to decrypt file")
    else:
        file_data = encrypted_data

    logger.info("Download: %s | IP: %s", original_name, request.client.host)

    return Response(
        content=file_data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{original_name}"'}
    )


@router.delete("/delete/{filename}", dependencies=[Depends(verify_token)])
@limiter.limit("20/minute")
async def delete_file(request: Request, filename: str):
    file_path = UPLOAD_FOLDER / filename
    if not file_path.resolve().is_relative_to(UPLOAD_FOLDER.resolve()):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    file_path.unlink()

    meta = load_metadata()
    meta.pop(filename, None)
    save_metadata(meta)

    logger.info("Deleted: %s", filename)
    return {"filename": filename, "message": "File deleted successfully"}