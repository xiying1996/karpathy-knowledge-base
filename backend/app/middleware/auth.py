import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

logger = logging.getLogger(__name__)


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if settings.API_KEY is None or settings.API_KEY == "":
            return await call_next(request)

        if request.url.path in ("/", "/api/health"):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if api_key is None:
            logger.warning(f"Missing API key for {request.client.host}")
            raise HTTPException(status_code=401, detail="Missing API key")

        if api_key != settings.API_KEY:
            logger.warning(f"Invalid API key for {request.client.host}")
            raise HTTPException(status_code=401, detail="Invalid API key")

        return await call_next(request)
