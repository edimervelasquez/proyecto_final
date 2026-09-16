import logging
import time
from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.security import validate_access_token


logger = logging.getLogger("backend.requests")


class RequestMiddleware(BaseHTTPMiddleware):
    PUBLIC_PATHS = {
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/auth/login",
        "/api/auth/registrar",
    }

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.perf_counter()

        if request.method != "OPTIONS" and request.url.path not in self.PUBLIC_PATHS:
            authorization = request.headers.get("Authorization", "")
            scheme, _, token = authorization.partition(" ")
            if scheme.lower() != "bearer" or not token:
                return self._unauthorized(request, start_time, "Token requerido.")

            try:
                request.state.token_payload = validate_access_token(token)
            except ValueError as exc:
                return self._unauthorized(request, start_time, str(exc))

        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "%s %s -> 500 (%.2f ms)",
                request.method,
                request.url.path,
                elapsed_ms,
            )
            raise

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "%s %s -> %s (%.2f ms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response

    @staticmethod
    def _unauthorized(request: Request, start_time: float, detail: str):
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.warning(
            "%s %s -> 401 (%.2f ms)",
            request.method,
            request.url.path,
            elapsed_ms,
        )
        return JSONResponse(status_code=401, content={"detail": detail})
