"""
Core logging functionality for Beacon.

This module provides the basic logging setup and configuration functions.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import structlog

from .config import LogConfig, LogLevel, LogFormat
from .formatters import StructuredFormatter, JSONFormatter
from .handlers import setup_handlers


def setup_logger(
    name: str,
    log_dir: Optional[Path] = None,
    debug: bool = False,
    config: Optional[LogConfig] = None,
) -> logging.Logger:
    """Sets up a standardized logger for the toolkit.

    Args:
        name: Name of the logger/module
        log_dir: Directory to store log files. If None, only console logging is enabled
        debug: Whether to enable debug logging
        config: Optional configuration object

    Returns:
        Configured logger instance
    """
    if config is None:
        config = LogConfig()
        config.level = LogLevel.DEBUG if debug else LogLevel.INFO
        if log_dir:
            from .config import FileHandlerConfig
            config.file = FileHandlerConfig(
                directory=log_dir,
                filename=log_dir / f"{name}.log",
                enabled=True
            )

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.level))

    # Close and clear any existing handlers
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    # Setup handlers based on configuration
    handlers = setup_handlers(config)
    for handler in handlers:
        logger.addHandler(handler)

    logger.propagate = config.propagate

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Name of the logger. If None, returns the root logger.
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def setup_structured_logging(
    config: Optional[LogConfig] = None,
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
) -> None:
    """Setup structured logging configuration using structlog.
    
    Args:
        config: Configuration object
        log_level: Override log level from config
        log_format: Override log format from config
    """
    if config is None:
        config = LogConfig()
    
    if log_level:
        config.level = LogLevel(log_level.upper())
    if log_format:
        config.format = LogFormat(log_format)
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, config.level.value),
    )
    
    # Configure structlog processors
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add renderer based on format
    if config.format == LogFormat.JSON:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_structured_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance.
    
    Args:
        name: Name of the logger
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


def setup_logging_from_dict(config_dict: Dict[str, Any]) -> logging.Logger:
    """Setup logging from a dictionary configuration.
    
    Args:
        config_dict: Dictionary containing logging configuration
        
    Returns:
        Configured logger instance
    """
    config = LogConfig(**config_dict)
    name = config.name or "beacon"
    
    return setup_logger(name, config=config)


def setup_logging_from_env() -> logging.Logger:
    """Setup logging from environment variables.
    
    Returns:
        Configured logger instance
    """
    import os
    
    config_dict = {
        "level": os.getenv("BEACON_LOG_LEVEL", "INFO"),
        "format": os.getenv("BEACON_LOG_FORMAT", "text"),
        "name": os.getenv("BEACON_LOG_NAME", "beacon"),
    }
    
    # Handle file logging
    log_dir = os.getenv("BEACON_LOG_DIR")
    if log_dir:
        config_dict["file"] = {
            "directory": Path(log_dir),
            "enabled": True,
        }
    
    return setup_logging_from_dict(config_dict)
