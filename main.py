from fastapi import FastAPI
import logging
from fastapi.staticfiles import StaticFiles
from routes import router
from utils import check_permissions
from config import UPLOAD_FOLDER

