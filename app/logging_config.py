import logging
import sys
from datetime import datetime
from typing import Any

from pythonjsonlogger.json import JsonFormatter

from app.config import get_settings

settings = get_settings()


class CustomJsonFormatter(JsonFormatter):
    """Custom JSON formatter para logs estructurados"""

    def add_fields(self, log_record: dict[str, Any], record: logging.LogRecord, message_dict: dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)

        # Agregar timestamp en formato ISO
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'

        # Agregar información del servicio
        log_record['service'] = 'ecommerce-api'
        log_record['version'] = '1.0.0'
        log_record['environment'] = settings.APP_ENV

        # Reorganizar campos para mejor legibilidad
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

        # Agregar información de contexto si está disponible
        if hasattr(record, 'user_id'):
            log_record['user_id'] = getattr(record, 'user_id', None)
        if hasattr(record, 'request_id'):
            log_record['request_id'] = getattr(record, 'request_id', None)
        if hasattr(record, 'endpoint'):
            log_record['endpoint'] = getattr(record, 'endpoint', None)
        if hasattr(record, 'method'):
            log_record['method'] = getattr(record, 'method', None)
        if hasattr(record, 'status_code'):
            log_record['status_code'] = getattr(record, 'status_code', None)
        if hasattr(record, 'duration'):
            log_record['duration_ms'] = getattr(record, 'duration', None)


def setup_logging() -> logging.Logger:
    """Configurar el sistema de logging estructurado"""

    # Crear logger principal
    logger = logging.getLogger("ecommerce-api")
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # Limpiar handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Crear handler para stdout
    handler = logging.StreamHandler(sys.stdout)

    # Configurar formato JSON
    formatter = CustomJsonFormatter(
        fmt='%(timestamp)s %(level)s %(name)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # Configurar nivel de logs según entorno
    if settings.APP_ENV == "development":
        logger.setLevel(logging.DEBUG)
        # También mostrar logs de SQLAlchemy en desarrollo
        sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
        sqlalchemy_logger.setLevel(logging.INFO)
        sqlalchemy_logger.addHandler(handler)
    elif settings.APP_ENV == "production":
        logger.setLevel(logging.WARNING)
    else:  # testing
        logger.setLevel(logging.ERROR)

    # Evitar duplicación de logs
    logger.propagate = False

    return logger


def get_logger(name: str = "ecommerce-api") -> logging.Logger:
    """Obtener un logger configurado"""
    return logging.getLogger(name)


# Funciones utilitarias para logging estructurado
def log_request(logger: logging.Logger, method: str, endpoint: str, user_id: int | None = None, request_id: str | None = None) -> None:
    """Log de inicio de request"""
    extra = {
        'method': method,
        'endpoint': endpoint,
        'event': 'request_start'
    }
    if user_id:
        extra['user_id'] = str(user_id)
    if request_id:
        extra['request_id'] = request_id

    logger.info(f"{method} {endpoint} - Request started", extra=extra)


def log_response(logger: logging.Logger, method: str, endpoint: str, status_code: int,
                duration_ms: float, user_id: int | None = None, request_id: str | None = None) -> None:
    """Log de respuesta completada"""
    extra = {
        'method': method,
        'endpoint': endpoint,
        'status_code': status_code,
        'duration': round(duration_ms, 2),
        'event': 'request_completed'
    }
    if user_id:
        extra['user_id'] = str(user_id)
    if request_id:
        extra['request_id'] = request_id

    level = logging.INFO if status_code < 400 else logging.WARNING if status_code < 500 else logging.ERROR
    logger.log(level, f"{method} {endpoint} - {status_code} ({duration_ms:.2f}ms)", extra=extra)


def log_error(logger: logging.Logger, error: Exception, context: dict[str, Any] | None = None) -> None:
    """Log de errores con contexto"""
    extra = {
        'event': 'error',
        'error_type': type(error).__name__,
        'error_message': str(error)
    }
    if context:
        extra.update(context)

    logger.error(f"Error: {error}", extra=extra, exc_info=True)


def log_business_event(logger: logging.Logger, event: str, details: dict[str, Any]) -> None:
    """Log de eventos de negocio importantes"""
    extra = {
        'event': 'business_event',
        'event_type': event,
        **details
    }

    logger.info(f"Business event: {event}", extra=extra)


def log_security_event(logger: logging.Logger, event: str, details: dict[str, Any]) -> None:
    """Log de eventos de seguridad"""
    extra = {
        'event': 'security_event',
        'event_type': event,
        **details
    }

    logger.warning(f"Security event: {event}", extra=extra)


def log_performance_metric(logger: logging.Logger, metric: str, value: float, unit: str = "ms",
                          context: dict[str, Any] | None = None) -> None:
    """Log de métricas de rendimiento"""
    extra = {
        'event': 'performance_metric',
        'metric_name': metric,
        'metric_value': value,
        'metric_unit': unit
    }
    if context:
        extra.update(context)

    logger.info(f"Performance metric: {metric} = {value} {unit}", extra=extra)
