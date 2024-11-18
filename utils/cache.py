from fastapi import FastAPI
import redis
import json
from functools import wraps
from typing import Optional, Callable
import os

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

def cache_response(expire_time_seconds: int = 300):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get cached response
            cached_response = redis_client.get(cache_key)
            if cached_response:
                return json.loads(cached_response)
            
            # If no cache, execute function and cache result
            response = await func(*args, **kwargs)
            redis_client.setex(
                cache_key,
                expire_time_seconds,
                json.dumps(response)
            )
            return response
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """Invalidate cache entries matching the pattern"""
    for key in redis_client.scan_iter(pattern):
        redis_client.delete(key)