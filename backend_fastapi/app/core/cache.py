"""
Caching Layer
Redis-based caching with safe fallback to in-memory
"""

from typing import Optional, Any, Callable
from functools import wraps
import json
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


# =====================================================
# Cache Backends
# =====================================================

class CacheBackend:
    async def get(self, key: str) -> Optional[str]:
        raise NotImplementedError

    async def set(self, key: str, value: str, ttl: int):
        raise NotImplementedError

    async def delete(self, key: str):
        raise NotImplementedError


class RedisCache(CacheBackend):
    def __init__(self):
        self._redis = None

    def _get_redis(self):
        if self._redis is None:
            import redis.asyncio as redis
            self._redis = redis.from_url(settings.REDIS_URL)
            logger.info("Redis cache initialized")
        return self._redis

    async def get(self, key: str) -> Optional[str]:
        try:
            value = await self._get_redis().get(key)
            return value.decode() if value else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: str, ttl: int):
        try:
            await self._get_redis().setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    async def delete(self, key: str):
        try:
            await self._get_redis().delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")


class InMemoryCache(CacheBackend):
    def __init__(self):
        self._cache: dict = {}

    async def get(self, key: str) -> Optional[str]:
        return self._cache.get(key)

    async def set(self, key: str, value: str, ttl: int):
        self._cache[key] = value

    async def delete(self, key: str):
        self._cache.pop(key, None)


# =====================================================
# Unified Cache Interface
# =====================================================

class Cache:
    def __init__(self):
        if settings.ENABLE_REDIS and settings.REDIS_URL:
            self.backend = RedisCache()
            logger.info("Using Redis cache")
        else:
            self.backend = InMemoryCache()
            logger.info("Using in-memory cache")

    async def get(self, key: str) -> Optional[Any]:
        value = await self.backend.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        ttl = ttl or settings.CACHE_TTL_DEFAULT

        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        elif not isinstance(value, str):
            value = str(value)

        await self.backend.set(key, value, ttl)

    async def delete(self, key: str):
        await self.backend.delete(key)

    def cached(self, ttl: Optional[int] = None, key_prefix: str = ""):
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_key = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"

                cached_value = await self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl)
                return result

            return wrapper
        return decorator


# Global cache instance
cache = Cache()

