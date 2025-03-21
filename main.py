from fastapi import FastAPI
import logging
from fastapi.staticfiles import StaticFiles
from routes import router
from utils import check_permissions
from config import UPLOAD_FOLDER

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)