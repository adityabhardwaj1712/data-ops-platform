"""
Caching Layer
Redis-based caching with fallback to in-memory
"""

from typing import Optional, Any, Callable
from functools import wraps
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheBackend:
    """Abstract cache backend."""
    
    async def get(self, key: str) -> Optional[str]:
        raise NotImplementedError
    
    async def set(self, key: str, value: str, ttl: int = 300):
        raise NotImplementedError
    
    async def delete(self, key: str):
        raise NotImplementedError


class RedisCache(CacheBackend):
    """Redis cache backend (lazy-loaded)."""
    
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
            redis = self._get_redis()
            value = await redis.get(key)
            return value.decode() if value else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: int = 300):
        try:
            redis = self._get_redis()
            await redis.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    async def delete(self, key: str):
        try:
            redis = self._get_redis()
            await redis.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")


class InMemoryCache(CacheBackend):
    """In-memory cache backend (fallback)."""
    
    def __init__(self):
        self._cache: dict = {}
    
    async def get(self, key: str) -> Optional[str]:
        return self._cache.get(key)
    
    async def set(self, key: str, value: str, ttl: int = 300):
        self._cache[key] = value
        # Note: TTL not implemented for in-memory (would need background task)
    
    async def delete(self, key: str):
        self._cache.pop(key, None)


class Cache:
    """
    Unified cache interface.
    
    Uses Redis if enabled, falls back to in-memory cache.
    """
    
    def __init__(self):
        if settings.ENABLE_REDIS:
            self.backend = RedisCache()
            logger.info("Using Redis cache")
        else:
            self.backend = InMemoryCache()
            logger.info("Using in-memory cache")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = await self.backend.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache."""
        if ttl is None:
            ttl = settings.CACHE_TTL_DEFAULT
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        elif not isinstance(value, str):
            value = str(value)
        
        await self.backend.set(key, value, ttl)
    
    async def delete(self, key: str):
        """Delete value from cache."""
        await self.backend.delete(key)
    
    def cached(self, ttl: int = None, key_prefix: str = ""):
        """
        Decorator for caching function results.
        
        Usage:
            @cache.cached(ttl=300, key_prefix="dataset")
            async def get_dataset(id):
                return await db.get(id)
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"
                
                # Try to get from cache
                cached_value = await self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Store in cache
                await self.set(cache_key, result, ttl)
                logger.debug(f"Cache set: {cache_key}")
                
                return result
            
            return wrapper
        return decorator


# Global cache instance
cache = Cache()
