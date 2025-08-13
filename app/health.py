"""
Health check endpoints para monitoreo
"""

import asyncio
import time
from typing import Any, Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import engine, get_database
from app.logging_config import get_logger, log_performance_metric
from app.redis_client import redis_client

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger("health-check")
settings = get_settings()


@router.get("/")
async def health_check():
    """Health check básico - siempre debe responder rápido"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "ecommerce-api",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
    }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_database)):
    """
    Readiness check - verifica que el servicio esté listo para recibir tráfico
    Incluye verificación de dependencias críticas
    """
    start_time = time.time()
    checks = {}
    overall_status = "ready"

    # Verificar base de datos
    db_status = await _check_database(db)
    checks["database"] = db_status
    if not db_status["healthy"]:
        overall_status = "not_ready"

    # Verificar Redis
    redis_status = await _check_redis()
    checks["redis"] = redis_status
    if not redis_status["healthy"]:
        overall_status = "not_ready"

    duration_ms = (time.time() - start_time) * 1000
    log_performance_metric(logger, "readiness_check_duration", duration_ms, "ms")

    response = {
        "status": overall_status,
        "timestamp": time.time(),
        "checks": checks,
        "duration_ms": round(duration_ms, 2),
    }

    if overall_status != "ready":
        raise HTTPException(status_code=503, detail=response)

    return response


@router.get("/live")
async def liveness_check():
    """
    Liveness check - verifica que el servicio esté corriendo
    No debe depender de servicios externos
    """
    return {
        "status": "alive",
        "timestamp": time.time(),
        "uptime_seconds": time.time() - _get_startup_time(),
    }


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_database)):
    """Health check detallado con métricas completas"""
    start_time = time.time()

    # Ejecutar todas las verificaciones en paralelo
    db_task = asyncio.create_task(_check_database_detailed(db))
    redis_task = asyncio.create_task(_check_redis_detailed())
    system_task = asyncio.create_task(_check_system())

    results = await asyncio.gather(
        db_task, redis_task, system_task, return_exceptions=True
    )
    db_result: Union[dict[str, Any], BaseException] = results[0]
    redis_result: Union[dict[str, Any], BaseException] = results[1]
    system_result: Union[dict[str, Any], BaseException] = results[2]

    # Determinar estado general
    checks = {
        "database": db_result
        if not isinstance(db_result, BaseException)
        else {"healthy": False, "error": str(db_result)},
        "redis": redis_result
        if not isinstance(redis_result, BaseException)
        else {"healthy": False, "error": str(redis_result)},
        "system": system_result
        if not isinstance(system_result, BaseException)
        else {"healthy": False, "error": str(system_result)},
    }

    overall_healthy = all(
        check.get("healthy", False) if isinstance(check, dict) else False
        for check in checks.values()
    )
    duration_ms = (time.time() - start_time) * 1000

    response = {
        "status": "healthy" if overall_healthy else "unhealthy",
        "timestamp": time.time(),
        "service": "ecommerce-api",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "uptime_seconds": time.time() - _get_startup_time(),
        "checks": checks,
        "duration_ms": round(duration_ms, 2),
    }

    if not overall_healthy:
        raise HTTPException(status_code=503, detail=response)

    return response


async def _check_database(db: AsyncSession) -> dict[str, Any]:
    """Verificación básica de base de datos"""
    try:
        start_time = time.time()
        await db.execute(text("SELECT 1"))
        duration_ms = (time.time() - start_time) * 1000

        return {
            "healthy": True,
            "response_time_ms": round(duration_ms, 2),
            "status": "connected",
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"healthy": False, "error": str(e), "status": "connection_failed"}


async def _check_database_detailed(db: AsyncSession) -> dict[str, Any]:
    """Verificación detallada de base de datos"""
    try:
        start_time = time.time()

        # Test de conexión básica
        _ = await db.execute(text("SELECT 1"))
        connection_time = time.time() - start_time

        # Test de escritura/lectura temporal
        test_start = time.time()
        await db.execute(text("SELECT COUNT(*) FROM users"))
        query_time = time.time() - test_start

        # Verificar pool de conexiones usando el engine importado
        pool_info = {}
        try:
            # Acceder al pool directamente desde el engine
            if hasattr(engine, "pool") and engine.pool is not None:
                pool = engine.pool
                # Usar getattr con defaults para manejar atributos que pueden no existir
                pool_info = {
                    "size": getattr(pool, "size", lambda: 0)(),
                    "checked_in": getattr(pool, "checkedin", lambda: 0)(),
                    "checked_out": getattr(pool, "checkedout", lambda: 0)(),
                    "overflow": getattr(pool, "overflow", lambda: 0)(),
                }
                pool_info["total"] = pool_info["size"] + pool_info["overflow"]
            else:
                pool_info = {"status": "Engine pool not available"}
        except (AttributeError, TypeError, Exception) as e:
            pool_info = {"error": f"Pool information not available: {str(e)}"}

        total_time = (time.time() - start_time) * 1000

        return {
            "healthy": True,
            "response_time_ms": round(total_time, 2),
            "connection_time_ms": round(connection_time * 1000, 2),
            "query_time_ms": round(query_time * 1000, 2),
            "pool_info": pool_info,
            "status": "fully_operational",
        }
    except Exception as e:
        logger.error(f"Detailed database health check failed: {e}")
        return {"healthy": False, "error": str(e), "status": "error"}


async def _check_redis() -> dict[str, Any]:
    """Verificación básica de Redis"""
    try:
        start_time = time.time()
        if await redis_client.is_connected():
            duration_ms = (time.time() - start_time) * 1000
            return {
                "healthy": True,
                "response_time_ms": round(duration_ms, 2),
                "status": "connected",
            }
        else:
            return {"healthy": False, "status": "not_connected"}
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {"healthy": False, "error": str(e), "status": "connection_failed"}


async def _check_redis_detailed() -> dict[str, Any]:
    """Verificación detallada de Redis"""
    try:
        start_time = time.time()

        # Test de conexión
        if not await redis_client.is_connected():
            return {"healthy": False, "status": "not_connected"}

        # Test de escritura/lectura
        test_key = "health_check_test"
        test_value = str(time.time())

        write_start = time.time()
        await redis_client.set(test_key, test_value, expire_seconds=60)
        write_time = time.time() - write_start

        read_start = time.time()
        retrieved_value = await redis_client.get(test_key)
        read_time = time.time() - read_start

        # Limpiar
        await redis_client.delete(test_key)

        # Verificar que el valor se escribió y leyó correctamente
        data_integrity = retrieved_value == test_value

        total_time = (time.time() - start_time) * 1000

        return {
            "healthy": data_integrity,
            "response_time_ms": round(total_time, 2),
            "write_time_ms": round(write_time * 1000, 2),
            "read_time_ms": round(read_time * 1000, 2),
            "data_integrity": data_integrity,
            "status": "fully_operational"
            if data_integrity
            else "data_integrity_failed",
        }
    except Exception as e:
        logger.error(f"Detailed Redis health check failed: {e}")
        return {"healthy": False, "error": str(e), "status": "error"}


async def _check_system() -> dict[str, Any]:
    """Verificación del sistema"""
    try:
        import os

        import psutil

        # Información de CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Información de memoria
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)

        # Información de disco
        disk = psutil.disk_usage("/")
        disk_percent = (disk.used / disk.total) * 100
        disk_free_gb = disk.free / (1024**3)

        # Información del proceso
        process = psutil.Process(os.getpid())
        process_memory_mb = process.memory_info().rss / (1024**2)

        # Determinar si el sistema está saludable
        healthy = (
            cpu_percent < 90
            and memory_percent < 90
            and disk_percent < 90
            and memory_available_gb > 0.1
            and disk_free_gb > 0.5
        )

        return {
            "healthy": healthy,
            "cpu_percent": round(cpu_percent, 1),
            "memory_percent": round(memory_percent, 1),
            "memory_available_gb": round(memory_available_gb, 2),
            "disk_percent": round(disk_percent, 1),
            "disk_free_gb": round(disk_free_gb, 2),
            "process_memory_mb": round(process_memory_mb, 1),
            "status": "healthy" if healthy else "resource_constrained",
        }
    except ImportError:
        # psutil no está instalado
        return {
            "healthy": True,
            "status": "monitoring_unavailable",
            "note": "Install psutil for detailed system monitoring",
        }
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        return {"healthy": False, "error": str(e), "status": "error"}


# Variable global para tiempo de inicio (se establece al importar)
_startup_time = time.time()


def _get_startup_time() -> float:
    """Obtener el tiempo de inicio del servicio"""
    return _startup_time
