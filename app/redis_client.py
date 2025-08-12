import json
from typing import Any

import redis.asyncio as redis

from app.config import get_settings

settings = get_settings()


class RedisClient:
    """Cliente Redis para manejar caché de manera simple"""

    def __init__(self):
        self.redis = None
        self._connected = False

    async def connect(self):
        """Conecta a Redis"""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Probar la conexión
            await self.redis.ping()
            self._connected = True
            print("Conectado a Redis exitosamente")
        except Exception as e:
            print(f"Error conectando a Redis: {e}")
            self._connected = False

    async def disconnect(self):
        """Desconecta de Redis"""
        if self.redis:
            await self.redis.close()
            self._connected = False
            print("Redis desconectado")

    async def is_connected(self) -> bool:
        """Verifica si Redis está conectado"""
        if not self._connected or not self.redis:
            return False
        try:
            await self.redis.ping()
            return True
        except Exception:
            self._connected = False
            return False

    async def set(
        self, key: str, value: Any, expire_seconds: int | None = None
    ) -> bool:
        """Guarda un valor en Redis"""
        if not await self.is_connected() or self.redis is None:
            return False

        try:
            # Convertir el valor a JSON si no es string
            if not isinstance(value, str):
                value = json.dumps(value, default=str)

            if expire_seconds:
                await self.redis.setex(key, expire_seconds, value)
            else:
                await self.redis.set(key, value)

            return True
        except Exception as e:
            print(f"Error guardando en Redis {key}: {e}")
            return False

    async def get(self, key: str) -> Any | None:
        """Obtiene un valor de Redis"""
        if not await self.is_connected() or self.redis is None:
            return None

        try:
            value = await self.redis.get(key)
            if value is None:
                return None

            # Intentar convertir de JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Si no es JSON, devolver como string
                return value

        except Exception as e:
            print(f"Error obteniendo de Redis {key}: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """Elimina una clave de Redis"""
        if not await self.is_connected() or self.redis is None:
            return False

        try:
            result = await self.redis.delete(key)
            return bool(result > 0)
        except Exception as e:
            print(f"Error eliminando de Redis {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Verifica si una clave existe"""
        if not await self.is_connected() or self.redis is None:
            return False

        try:
            result = await self.redis.exists(key)
            return bool(result > 0)
        except Exception as e:
            print(f"Error verificando existencia en Redis {key}: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> int | None:
        """Incrementa un contador"""
        if not await self.is_connected() or self.redis is None:
            return None

        try:
            result = await self.redis.incrby(key, amount)
            return int(result) if result is not None else None
        except Exception as e:
            print(f"Error incrementando en Redis {key}: {e}")
            return None

    async def set_with_ttl(self, key: str, value: Any, seconds: int) -> bool:
        """Guarda un valor con tiempo de vida específico"""
        return await self.set(key, value, expire_seconds=seconds)

    async def get_ttl(self, key: str) -> int | None:
        """Obtiene el tiempo de vida restante de una clave"""
        if not await self.is_connected() or self.redis is None:
            return None

        try:
            ttl = await self.redis.ttl(key)
            return ttl if ttl >= 0 else None
        except Exception as e:
            print(f"Error obteniendo TTL de Redis {key}: {e}")
            return None


# Instancia global del cliente Redis
redis_client = RedisClient()


# Funciones de ayuda para usar Redis de manera simple
async def cache_set(key: str, value: Any, expire_minutes: int = 15) -> bool:
    """Guarda algo en caché por X minutos"""
    return await redis_client.set(key, value, expire_minutes * 60)


async def cache_get(key: str) -> Any | None:
    """Obtiene algo del caché"""
    return await redis_client.get(key)


async def cache_delete(key: str) -> bool:
    """Elimina algo del caché"""
    return await redis_client.delete(key)


async def cache_products(
    products: list, filters: dict, expire_minutes: int = 10
) -> bool:
    """Guarda productos en caché con sus filtros"""
    # Crear una clave única basada en los filtros
    filter_key = "_".join(
        [f"{k}_{v}" for k, v in sorted(filters.items()) if v is not None]
    )
    cache_key = f"products:{filter_key}"

    return await cache_set(cache_key, products, expire_minutes)


async def get_cached_products(filters: dict) -> list | None:
    """Obtiene productos del caché"""
    filter_key = "_".join(
        [f"{k}_{v}" for k, v in sorted(filters.items()) if v is not None]
    )
    cache_key = f"products:{filter_key}"

    return await cache_get(cache_key)


async def cache_user(user_id: int, user_data: dict, expire_minutes: int = 30) -> bool:
    """Guarda datos de usuario en caché"""
    cache_key = f"user:{user_id}"
    return await cache_set(cache_key, user_data, expire_minutes)


async def get_cached_user(user_id: int) -> dict | None:
    """Obtiene datos de usuario del caché"""
    cache_key = f"user:{user_id}"
    return await cache_get(cache_key)


async def invalidate_user_cache(user_id: int) -> bool:
    """Elimina el caché de un usuario cuando se actualiza"""
    cache_key = f"user:{user_id}"
    return await cache_delete(cache_key)


# Funciones para el Rate Limiting
async def check_rate_limit(
    user_ip: str, limit: int = 100, window_seconds: int = 60
) -> dict:
    """
    Verifica si un usuario ha excedido el límite de peticiones

    Returns:
        dict con: allowed (bool), remaining (int), reset_time (int)
    """
    if not await redis_client.is_connected() or redis_client.redis is None:
        # Si Redis no está disponible, permitir todas las peticiones
        return {"allowed": True, "remaining": limit, "reset_time": 0}

    try:
        key = f"rate_limit:{user_ip}"
        current_time = int(__import__("time").time())
        window_start = current_time - window_seconds

        # Limpiar requests antiguos y contar los actuales
        await redis_client.redis.zremrangebyscore(key, 0, window_start)
        current_requests = await redis_client.redis.zcard(key)

        if current_requests >= limit:
            # Límite excedido
            ttl = await redis_client.redis.ttl(key)
            reset_time = current_time + (ttl if ttl > 0 else window_seconds)
            return {"allowed": False, "remaining": 0, "reset_time": reset_time}

        # Agregar esta petición
        await redis_client.redis.zadd(key, {str(current_time): current_time})
        await redis_client.redis.expire(key, window_seconds)

        remaining = limit - current_requests - 1
        return {
            "allowed": True,
            "remaining": remaining,
            "reset_time": current_time + window_seconds,
        }

    except Exception as e:
        print(f"Error en rate limiting: {e}")
        # En caso de error, permitir la petición
        return {"allowed": True, "remaining": limit, "reset_time": 0}
