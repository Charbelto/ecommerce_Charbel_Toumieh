from fastapi import HTTPException
from typing import Optional, Dict, Any

class BaseServiceException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        service: str,
        additional_info: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.service = service
        self.additional_info = additional_info or {}

class ResourceNotFoundException(BaseServiceException):
    def __init__(self, resource: str, service: str, resource_id: Any):
        super().__init__(
            status_code=404,
            detail=f"{resource} not found",
            error_code="RESOURCE_NOT_FOUND",
            service=service,
            additional_info={"resource_id": str(resource_id)}
        )

class InsufficientFundsException(BaseServiceException):
    def __init__(self, username: str, required: float, available: float):
        super().__init__(
            status_code=400,
            detail="Insufficient funds for transaction",
            error_code="INSUFFICIENT_FUNDS",
            service="customer",
            additional_info={
                "username": username,
                "required_amount": required,
                "available_amount": available
            }
        )

class InvalidVersionException(BaseServiceException):
    def __init__(self, version: str, supported_versions: list):
        super().__init__(
            status_code=400,
            detail="Unsupported API version",
            error_code="INVALID_VERSION",
            service="all",
            additional_info={
                "requested_version": version,
                "supported_versions": supported_versions
            }
        )