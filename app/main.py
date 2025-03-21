from fastapi import FastAPI
import logging
from fastapi.staticfiles import StaticFiles
from app.routes import router
from app.utils import check_permissions
from app.config import UPLOAD_FOLDER

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

check_permissions(UPLOAD_FOLDER)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)