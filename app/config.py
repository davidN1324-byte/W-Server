from pathlib import Path

UPLOAD_FOLDER = Path(__file__).parent.parent / "uploads"
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}
ALLOWED_MIMES = {"text/plain", "application/pdf", "image/png", "image/jpeg", "image/gif"}
