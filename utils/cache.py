from fastapi import FastAPI
import redis
import json
from functools import wraps
from typing import Optional, Callable
import os
import fakeredis
from pydantic import BaseModel

redis_client = fakeredis.FakeStrictRedis()

def cache_response(expire_time_seconds=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached_response = redis_client.get(cache_key)
            
            if cached_response:
                return json.loads(cached_response.decode('utf-8'))
                
            response = await func(*args, **kwargs)
            
            # Convert response to dict if it's a Pydantic model or SQLAlchemy model
            if hasattr(response, 'model_dump'):
                response_data = response.model_dump()
            elif hasattr(response, '__dict__'):
                response_data = {
                    key: value for key, value in response.__dict__.items() 
                    if not key.startswith('_')
                }
            else:
                response_data = response
                
            redis_client.setex(cache_key, expire_time_seconds, json.dumps(response_data))
            return response
            
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """Invalidate cache entries matching the pattern"""
    for key in redis_client.scan_iter(pattern):
        redis_client.delete(key)