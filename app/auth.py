import logging
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from app.config import ACCESS_TOKEN

logger = logging.getLogger(__name__)
api_key_header = APIKeyHeader(name="X-Access-Token", auto_error=False)

def verify_token(token: str = Security(api_key_header)):
    if not ACCESS_TOKEN:
        raise HTTPException(status_code=500, detail="ACCESS_TOKEN not configured")
    match = bool(token) and token.strip() == ACCESS_TOKEN.strip()
    logger.info("Token check: %s", match)
    if not match:
        raise HTTPException(status_code=403, detail="Invalid token")