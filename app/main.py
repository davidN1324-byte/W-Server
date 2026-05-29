from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
import os
from datetime import datetime, timedelta
from app.routes import router
from app.utils import check_permissions, load_metadata, save_metadata
from app.config import UPLOAD_FOLDER, ACCESS_TOKEN, MAX_CONNECTIONS, FILE_TTL_HOURS

LOG_FILE = "logs/server.log"
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)


# ── Connection limiter middleware ──
class ConnectionLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_connections: int):
        super().__init__(app)
        self.max_connections = max_connections
        self._active = 0

    async def dispatch(self, request, call_next):
        if self._active >= self.max_connections:
            return JSONResponse(status_code=503, content={"detail": "Too many connections"})
        self._active += 1
        try:
            return await call_next(request)
        finally:
            self._active -= 1


# ── Auto-delete task ──
async def auto_cleanup():
    if not FILE_TTL_HOURS:
        return
    while True:
        await asyncio.sleep(3600)
        try:
            meta = load_metadata()
            cutoff = datetime.utcnow() - timedelta(hours=FILE_TTL_HOURS)
            to_delete = []

            for stored, value in meta.items():
                if not isinstance(value, dict):
                    continue
                uploaded_at = value.get("uploaded_at", "")
                if not uploaded_at:
                    continue
                try:
                    file_time = datetime.strptime(uploaded_at, "%Y-%m-%d %H:%M")
                    if file_time < cutoff:
                        to_delete.append(stored)
                except ValueError:
                    continue

            for stored in to_delete:
                file_path = UPLOAD_FOLDER / stored
                if file_path.exists():
                    file_path.unlink()
                    logger.info("Auto-deleted (TTL): %s", stored)
                meta.pop(stored, None)

            if to_delete:
                save_metadata(meta)

        except Exception as e:
            logger.error("Auto-cleanup error: %s", e)


limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    check_permissions(UPLOAD_FOLDER)
    logger.info("=" * 48)
    logger.info("Server started")
    logger.info("ACCESS_TOKEN: %s****", ACCESS_TOKEN[:6])
    logger.info("MAX_CONNECTIONS: %d", MAX_CONNECTIONS)
    if FILE_TTL_HOURS:
        logger.info("FILE_TTL_HOURS: %d", FILE_TTL_HOURS)
        asyncio.create_task(auto_cleanup())
    else:
        logger.info("FILE_TTL_HOURS: disabled")
    logger.info("=" * 48)
    yield


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(ConnectionLimitMiddleware, max_connections=MAX_CONNECTIONS)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)


# ── Security headers ──
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response