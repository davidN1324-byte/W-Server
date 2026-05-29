from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

UPLOAD_FOLDER = Path(__file__).parent.parent / "uploads"
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 100 * 1024 * 1024))
ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "txt,pdf,png,jpg,jpeg,gif").split(","))
ALLOWED_MIMES = set(os.getenv("ALLOWED_MIMES", "text/plain,application/pdf,image/png,image/jpeg,image/gif").split(","))
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")
MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", 10))
FILE_TTL_HOURS = int(os.getenv("FILE_TTL_HOURS", 0))
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")