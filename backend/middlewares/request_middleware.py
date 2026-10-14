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
    ADMIN_ONLY_PATHS = (
        "/api/dashboard",
        "/api/auth/usuarios",
    )
    WORKER_PATHS = (
        "/api/insumos",
        "/api/produccion",
    )
    SELLER_PATHS = (
        "/api/ventas",
        "/api/inventario",
        "/api/comercial/productos",
    )

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.perf_counter()

        if request.method != "OPTIONS" and request.url.path not in self.PUBLIC_PATHS:
            authorization = request.headers.get("Authorization", "")
            scheme, _, token = authorization.partition(" ")
            if scheme.lower() != "bearer" or not token:
                return self._unauthorized(request, start_time, "Token requerido.")

            try:
                payload = validate_access_token(token)
                request.state.token_payload = payload
            except ValueError as exc:
                return self._unauthorized(request, start_time, str(exc))

            role = str(payload.get("role", "")).upper()
            path = request.url.path
            allowed = None
            if (
                path.startswith("/api/insumos/")
                and path.endswith("/stock-minimo")
                and request.method == "PUT"
            ):
                allowed = {"ADMINISTRADOR"}
            elif any(path.startswith(prefix) for prefix in self.ADMIN_ONLY_PATHS):
                allowed = {"ADMINISTRADOR"}
            elif any(path.startswith(prefix) for prefix in self.WORKER_PATHS):
                allowed = {"ADMINISTRADOR", "TRABAJADOR"}
            elif any(path.startswith(prefix) for prefix in self.SELLER_PATHS):
                allowed = {"ADMINISTRADOR", "VENDEDOR"}
                if path.startswith("/api/inventario") and request.method != "GET":
                    allowed = {"ADMINISTRADOR"}
                if (
                    path.startswith("/api/comercial/productos/")
                    and request.method != "GET"
                ):
                    allowed = {"ADMINISTRADOR"}
            if allowed is not None and role not in allowed:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Tu rol no tiene permiso para esta operación."},
                )

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
