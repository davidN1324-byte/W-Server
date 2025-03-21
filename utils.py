import os
import hashlib
import magic
from pathlib import Path
from fastapi import HTTPException
from config import UPLOAD_FOLDER