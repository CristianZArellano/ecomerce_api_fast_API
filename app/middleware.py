import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.exceptions import EcommerceError, RateLimitError
from app.logging_config import (
    get_logger,
    log_error,
    log_request,
    log_response,
    log_security_event,
)
from app.redis_client import check_rate_limit


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging estructurado de requests"""

    def __init__(self, app, logger_name: str = "ecommerce-api"):
        super().__init__(app)
        self.logger = get_logger(logger_name)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Generar ID único para el request
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Extraer información del usuario si está disponible
        user_id = getattr(request.state, 'user_id', None)

        # Log de inicio del request
        start_time = time.time()
        log_request(
            self.logger,
            method=request.method,
            endpoint=str(request.url.path),
            user_id=user_id,
            request_id=request_id
        )

        try:
            # Procesar el request
            response = await call_next(request)

            # Calcular duración
            duration_ms = (time.time() - start_time) * 1000

            # Log de respuesta
            log_response(
                self.logger,
                method=request.method,
                endpoint=str(request.url.path),
                status_code=response.status_code,
                duration_ms=duration_ms,
                user_id=user_id,
                request_id=request_id
            )

            # Agregar headers de respuesta útiles
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

            return response

        except Exception as exc:
            # Calcular duración incluso para errores
            duration_ms = (time.time() - start_time) * 1000

            # Log del error
            log_error(
                self.logger,
                error=exc,
                context={
                    'method': request.method,
                    'endpoint': str(request.url.path),
                    'user_id': user_id,
                    'request_id': request_id,
                    'duration': duration_ms
                }
            )

            # Re-raise para que lo maneje el error handler
            raise exc


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware para rate limiting"""

    def __init__(self, app, logger_name: str = "ecommerce-api"):
        super().__init__(app)
        self.logger = get_logger(logger_name)

        # Configuración de rate limiting por endpoint
        self.rate_limits = {
            "/auth/login": {"limit": 5, "window": 300},      # 5 intentos por 5 min
            "/auth/register": {"limit": 3, "window": 3600},   # 3 intentos por hora
            "/auth/refresh": {"limit": 10, "window": 300},    # 10 intentos por 5 min
            "default": {"limit": 100, "window": 60}           # 100 requests por minuto
        }

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Obtener IP del cliente
        client_ip = self._get_client_ip(request)
        endpoint = str(request.url.path)

        # Determinar límites para este endpoint
        limits = self.rate_limits.get(endpoint, self.rate_limits["default"])

        # Verificar rate limit
        try:
            rate_limit_result = await check_rate_limit(
                user_ip=client_ip,
                limit=limits["limit"],
                window_seconds=limits["window"]
            )

            if not rate_limit_result["allowed"]:
                # Log del evento de seguridad
                log_security_event(
                    self.logger,
                    event="rate_limit_exceeded",
                    details={
                        "client_ip": client_ip,
                        "endpoint": endpoint,
                        "limit": limits["limit"],
                        "window_seconds": limits["window"],
                        "reset_time": rate_limit_result["reset_time"]
                    }
                )

                raise RateLimitError(
                    limit=limits["limit"],
                    window_seconds=limits["window"],
                    retry_after=rate_limit_result["reset_time"] - int(time.time())
                )

            # Agregar headers de rate limiting
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(limits["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_limit_result["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_limit_result["reset_time"])

            return response

        except RateLimitError:
            # Re-raise rate limit exceptions
            raise
        except Exception as exc:
            # Log error pero continúa (rate limiting no debe romper la app)
            log_error(
                self.logger,
                error=exc,
                context={
                    "middleware": "rate_limit",
                    "client_ip": client_ip,
                    "endpoint": endpoint
                }
            )
            return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """Extraer la IP real del cliente considerando proxies"""
        # Verificar headers de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fallback a la IP directa
        return str(request.client.host) if request.client else "unknown"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para agregar headers de seguridad"""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)

        # Headers de seguridad
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self'",
            "connect-src 'self'",
            "frame-ancestors 'none'"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # HSTS (solo para producción con HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware para manejo global de errores"""

    def __init__(self, app, logger_name: str = "ecommerce-api"):
        super().__init__(app)
        self.logger = get_logger(logger_name)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        try:
            return await call_next(request)
        except EcommerceError as exc:
            # Errores de aplicación - ya están bien formateados
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "code": exc.error_code,
                        "message": exc.message,
                        "details": exc.details
                    },
                    "request_id": getattr(request.state, 'request_id', None)
                },
                headers=self._get_error_headers(exc)
            )
        except ValueError as exc:
            # Errores de validación de datos
            log_error(
                self.logger,
                error=exc,
                context={"error_type": "validation", "endpoint": str(request.url.path)}
            )
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": str(exc),
                        "details": {}
                    },
                    "request_id": getattr(request.state, 'request_id', None)
                }
            )
        except Exception as exc:
            # Errores no controlados
            log_error(
                self.logger,
                error=exc,
                context={
                    "error_type": "unhandled",
                    "endpoint": str(request.url.path),
                    "method": request.method
                }
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An internal server error occurred",
                        "details": {}
                    },
                    "request_id": getattr(request.state, 'request_id', None)
                }
            )

    def _get_error_headers(self, exc: EcommerceError) -> dict:
        """Obtener headers específicos para ciertos tipos de error"""
        headers = {}

        if isinstance(exc, RateLimitError):
            headers["Retry-After"] = str(exc.details.get("retry_after", 60))

        return headers
