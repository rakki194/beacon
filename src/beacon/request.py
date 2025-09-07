"""
Request logging utilities for Beacon.
"""

import logging
import time
from typing import Any, Dict, Optional

import structlog

from .config import RequestLoggingConfig


class RequestLogger:
    """Handles request logging with structured data."""

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        config: Optional[RequestLoggingConfig] = None,
    ):
        self.logger = logger or logging.getLogger("requests")
        self.config = config or RequestLoggingConfig()

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        body: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Log a complete HTTP request.

        Args:
            method: HTTP method
            path: Request path
            status_code: HTTP status code
            duration: Request duration in seconds
            user_agent: User agent string
            ip_address: Client IP address
            headers: Request headers
            query_params: Query parameters
            body: Request body
            user_id: User ID for tracking
            session_id: Session ID for tracking
            request_id: Request ID for tracking
            **kwargs: Additional context information
        """
        log_data = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration * 1000,
            "duration_seconds": duration,
        }

        # Add optional fields based on configuration
        if self.config.log_headers and headers:
            # Filter out sensitive headers
            safe_headers = {
                k: v
                for k, v in headers.items()
                if k.lower() not in self.config.sensitive_headers
            }
            log_data["headers"] = safe_headers

        if self.config.log_query_params and query_params:
            log_data["query_params"] = query_params

        if self.config.log_body and body:
            log_data["body"] = body

        if user_agent:
            log_data["user_agent"] = user_agent

        if ip_address:
            log_data["ip_address"] = ip_address

        # Add tracking information
        if user_id:
            log_data["user_id"] = user_id
        if session_id:
            log_data["session_id"] = session_id
        if request_id:
            log_data["request_id"] = request_id

        # Add additional context
        log_data.update(kwargs)

        # Log based on status code
        if status_code >= 500:
            self.logger.error(
                f"HTTP {method} {path} - {status_code} ({duration:.3f}s)",
                extra=log_data,
            )
        elif status_code >= 400:
            self.logger.warning(
                f"HTTP {method} {path} - {status_code} ({duration:.3f}s)",
                extra=log_data,
            )
        else:
            self.logger.info(
                f"HTTP {method} {path} - {status_code} ({duration:.3f}s)",
                extra=log_data,
            )


def log_request_info(
    logger: structlog.BoundLogger,
    request_info: Dict[str, Any],
) -> None:
    """Log request information in a structured format.

    This function maintains compatibility with the original implementation.

    Args:
        logger: Structured logger instance
        request_info: Dictionary containing request information
    """
    logger.info(
        "HTTP request",
        method=request_info.get("method"),
        path=request_info.get("path"),
        status_code=request_info.get("status_code"),
        duration=request_info.get("duration"),
        user_agent=request_info.get("user_agent"),
        ip_address=request_info.get("ip_address"),
    )


def setup_request_logging(
    logger: Optional[logging.Logger] = None,
    config: Optional[RequestLoggingConfig] = None,
) -> RequestLogger:
    """Setup request logging.

    Args:
        logger: Logger instance to use
        config: Request logging configuration

    Returns:
        Configured request logger
    """
    return RequestLogger(logger, config)


class RequestMiddleware:
    """Middleware for automatically logging HTTP requests."""

    def __init__(
        self,
        logger: Optional[RequestLogger] = None,
        config: Optional[RequestLoggingConfig] = None,
    ):
        self.logger = logger or RequestLogger(config=config)

    def __call__(self, request, response, duration: float, **kwargs):
        """Log request and response information.

        Args:
            request: Request object (should have method, path, headers, etc.)
            response: Response object (should have status_code)
            duration: Request duration in seconds
            **kwargs: Additional context
        """
        # Extract request information
        method = getattr(request, "method", "UNKNOWN")
        path = getattr(request, "path", "/")
        headers = getattr(request, "headers", {})
        user_agent = headers.get("User-Agent")
        ip_address = getattr(request, "client_ip", None)

        # Extract response information
        status_code = getattr(response, "status_code", 200)

        # Extract tracking information
        user_id = getattr(request, "user_id", None)
        session_id = getattr(request, "session_id", None)
        request_id = getattr(request, "request_id", None)

        # Log the request
        self.logger.log_request(
            method=method,
            path=path,
            status_code=status_code,
            duration=duration,
            user_agent=user_agent,
            ip_address=ip_address,
            headers=headers,
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            **kwargs,
        )


def create_request_middleware(
    logger: Optional[RequestLogger] = None,
    config: Optional[RequestLoggingConfig] = None,
) -> RequestMiddleware:
    """Create a request middleware instance.

    Args:
        logger: Request logger instance
        config: Request logging configuration

    Returns:
        Request middleware instance
    """
    return RequestMiddleware(logger, config)
