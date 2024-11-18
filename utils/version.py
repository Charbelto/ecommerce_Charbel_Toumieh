from fastapi import FastAPI, Request
from typing import Callable, Dict, Any
from .exceptions import InvalidVersionException

class VersionedAPI:
    def __init__(self, app: FastAPI):
        self.app = app
        self.versions: Dict[str, Dict[str, Callable]] = {}
        
    def version(self, version_number: str):
        def decorator(func: Callable):
            endpoint = func.__name__
            if version_number not in self.versions:
                self.versions[version_number] = {}
            self.versions[version_number][endpoint] = func
            return func
        return decorator
    
    def get_versioned_endpoint(self, version: str, endpoint: str) -> Callable:
        if version not in self.versions or endpoint not in self.versions[version]:
            supported_versions = list(self.versions.keys())
            raise InvalidVersionException(version, supported_versions)
        return self.versions[version][endpoint]

    async def version_middleware(self, request: Request, call_next):
        version = request.headers.get("API-Version", "v1")
        request.state.api_version = version
        response = await call_next(request)
        response.headers["API-Version"] = version
        return response