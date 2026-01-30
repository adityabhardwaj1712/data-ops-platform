import time
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("dataops.middleware")
logging.basicConfig(level=logging.INFO)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every incoming request with response status and execution time
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = round(time.time() - start_time, 4)
        logger.info(
            f"{request.method} {request.url.path} "
            f"-> {response.status_code} [{duration}s]"
        )

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handler to prevent API crashes
    """

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.exception("Unhandled server error")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Internal Server Error",
                    "details": str(exc),
                },
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Placeholder rate limiter.
    Safe no-op for now.
    Can be upgraded later with Redis / token bucket.
    """

    async def dispatch(self, request: Request, call_next):
        # Future logic goes here
        return await call_next(request)
