from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .exceptions import BaseServiceException

def setup_error_handlers(app: FastAPI):
    @app.exception_handler(BaseServiceException)
    async def service_exception_handler(request: Request, exc: BaseServiceException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.detail,
                    "service": exc.service,
                    "additional_info": exc.additional_info
                }
            }
        )