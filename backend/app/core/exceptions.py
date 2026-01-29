"""
Custom Exception Classes
Structured error handling for better API responses
"""
from fastapi import HTTPException, status


class DataOpsException(HTTPException):
    """Base exception for DataOps platform"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        extra: dict = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code or f"ERROR_{status_code}"
        self.extra = extra or {}


class ValidationError(DataOpsException):
    """Schema or data validation error"""
    
    def __init__(self, detail: str, field: str = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="VALIDATION_ERROR",
            extra={"field": field} if field else {}
        )


class NotFoundError(DataOpsException):
    """Resource not found"""
    
    def __init__(self, resource_type: str, resource_id: str = None):
        detail = f"{resource_type} not found"
        if resource_id:
            detail += f": {resource_id}"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND",
            extra={"resource_type": resource_type, "resource_id": resource_id}
        )


class RateLimitError(DataOpsException):
    """Rate limit exceeded"""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            error_code="RATE_LIMIT_EXCEEDED",
            extra={"retry_after": retry_after}
        )


class ScrapingError(DataOpsException):
    """Scraping operation failed"""
    
    def __init__(self, detail: str, url: str = None, reason: str = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="SCRAPING_ERROR",
            extra={"url": url, "reason": reason}
        )


class RobotsTxtError(DataOpsException):
    """Robots.txt violation"""
    
    def __init__(self, domain: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Scraping not allowed for {domain} (robots.txt)",
            error_code="ROBOTS_TXT_VIOLATION",
            extra={"domain": domain}
        )


class DatabaseError(DataOpsException):
    """Database operation failed"""
    
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR"
        )
