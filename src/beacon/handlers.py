"""
Custom handlers for Beacon logging framework.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import List, Optional

from .config import LogConfig, LogFormat, LogLevel
from .formatters import (
    ColoredFormatter,
    JSONFormatter,
    StructuredFormatter,
    TextFormatter,
)


class RotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Enhanced rotating file handler with better configuration."""

    def __init__(
        self,
        filename: str,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        encoding: Optional[str] = None,
        delay: bool = False,
        errors: Optional[str] = None,
        formatter: Optional[logging.Formatter] = None,
    ):
        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        super().__init__(
            filename=filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=encoding,
            delay=delay,
            errors=errors,
        )

        if formatter:
            self.setFormatter(formatter)


class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """Enhanced timed rotating file handler with better configuration."""

    def __init__(
        self,
        filename: str,
        when: str = "midnight",
        interval: int = 1,
        backup_count: int = 30,
        encoding: Optional[str] = None,
        delay: bool = False,
        errors: Optional[str] = None,
        formatter: Optional[logging.Formatter] = None,
    ):
        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        super().__init__(
            filename=filename,
            when=when,
            interval=interval,
            backupCount=backup_count,
            encoding=encoding,
            delay=delay,
            errors=errors,
        )

        if formatter:
            self.setFormatter(formatter)


class ConsoleHandler(logging.StreamHandler):
    """Enhanced console handler with color support."""

    def __init__(
        self,
        stream=None,
        use_colors: bool = True,
        formatter: Optional[logging.Formatter] = None,
    ):
        if stream is None:
            stream = sys.stdout

        super().__init__(stream)

        if formatter is None and use_colors:
            formatter = ColoredFormatter()
        elif formatter is None:
            formatter = TextFormatter()

        self.setFormatter(formatter)


def setup_handlers(config: LogConfig) -> List[logging.Handler]:
    """Setup handlers based on configuration.

    Args:
        config: Logging configuration

    Returns:
        List of configured handlers
    """
    handlers = []

    # Console handler
    if config.console.enabled:
        console_handler = ConsoleHandler(
            stream=sys.stderr if config.console.stream == "stderr" else sys.stdout,
            use_colors=config.console.stream == "stdout",
        )
        console_handler.setLevel(getattr(logging, config.console.level.value))

        # Set formatter based on format
        if config.console.format == LogFormat.JSON:
            console_handler.setFormatter(JSONFormatter())
        elif config.console.format == LogFormat.STRUCTURED:
            console_handler.setFormatter(StructuredFormatter())
        else:
            console_handler.setFormatter(TextFormatter())

        handlers.append(console_handler)

    # File handler
    if config.file and config.file.enabled:
        if config.file.filename:
            filename = config.file.filename
        elif config.file.directory:
            filename = config.file.directory / f"{config.name or 'beacon'}.log"
        else:
            raise ValueError(
                "Either filename or directory must be specified for file handler"
            )

        # Create directory if it doesn't exist
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        # Choose handler type based on configuration
        if config.file.when:
            # Timed rotating handler
            file_handler = TimedRotatingFileHandler(
                filename=str(filename),
                when=config.file.when,
                interval=config.file.interval or 1,
                backup_count=config.file.backup_count,
            )
        else:
            # Size-based rotating handler
            file_handler = RotatingFileHandler(
                filename=str(filename),
                max_bytes=config.file.max_bytes,
                backup_count=config.file.backup_count,
            )

        file_handler.setLevel(getattr(logging, config.file.level.value))

        # Set formatter based on format
        if config.file.format == LogFormat.JSON:
            file_handler.setFormatter(JSONFormatter())
        elif config.file.format == LogFormat.STRUCTURED:
            file_handler.setFormatter(StructuredFormatter())
        else:
            file_handler.setFormatter(TextFormatter())

        handlers.append(file_handler)

    return handlers


def setup_error_handler(
    log_dir: Path,
    max_bytes: int = 5 * 1024 * 1024,  # 5MB
    backup_count: int = 3,
) -> logging.Handler:
    """Setup a dedicated error handler.

    Args:
        log_dir: Directory for error logs
        max_bytes: Maximum file size before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured error handler
    """
    error_file = log_dir / "errors.log"
    error_handler = RotatingFileHandler(
        filename=str(error_file),
        max_bytes=max_bytes,
        backup_count=backup_count,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(StructuredFormatter())

    return error_handler


def setup_performance_handler(
    log_dir: Path,
    max_bytes: int = 5 * 1024 * 1024,  # 5MB
    backup_count: int = 3,
) -> logging.Handler:
    """Setup a dedicated performance handler.

    Args:
        log_dir: Directory for performance logs
        max_bytes: Maximum file size before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured performance handler
    """
    perf_file = log_dir / "performance.log"
    perf_handler = RotatingFileHandler(
        filename=str(perf_file),
        max_bytes=max_bytes,
        backup_count=backup_count,
    )
    perf_handler.setLevel(logging.INFO)
    perf_handler.setFormatter(JSONFormatter())

    return perf_handler


def setup_request_handler(
    log_dir: Path,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> logging.Handler:
    """Setup a dedicated request handler.

    Args:
        log_dir: Directory for request logs
        max_bytes: Maximum file size before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured request handler
    """
    request_file = log_dir / "requests.log"
    request_handler = RotatingFileHandler(
        filename=str(request_file),
        max_bytes=max_bytes,
        backup_count=backup_count,
    )
    request_handler.setLevel(logging.INFO)
    request_handler.setFormatter(JSONFormatter())

    return request_handler
