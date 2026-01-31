from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger("dataops.middleware")
logging.basicConfig(level=logging.INFO)


# =========================
# Request Logging Middleware
# =========================
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"{request.method} {request.url.path} "
            f"→ {response.status_code} "
            f"[{process_time:.2f}ms]"
        )

        response.headers["X-Process-Time-ms"] = str(round(process_time, 2))
        return response


# =========================
# Global Error Handling
# =========================
class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.exception("Unhandled exception occurred")

            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Internal Server Error",
                    "detail": str(exc),
                },
            )


# =========================
# Simple Rate Limit Middleware
# (safe default – NOT strict)
# =========================
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100):
        super().__init__(app)
        self.max_requests = max_requests
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"

        now = time.time()
        window = 60  # seconds

        timestamps = self.requests.get(ip, [])
        timestamps = [t for t in timestamps if now - t < window]

        if len(timestamps) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "Too Many Requests",
                },
            )

        timestamps.append(now)
        self.requests[ip] = timestamps

        return await call_next(request)
