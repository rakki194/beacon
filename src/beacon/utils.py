"""
Utility functions for Beacon logging framework.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import threading
import time

from .config import LogConfig, PerformanceConfig
from .handlers import (
    setup_error_handler,
    setup_performance_handler,
    setup_request_handler,
    RotatingFileHandler,
    TimedRotatingFileHandler,
)
from .performance import setup_performance_logging


def setup_log_rotation(
    log_dir: Path,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    when: Optional[str] = None,
    interval: int = 1,
) -> None:
    """Setup log rotation for all loggers.
    
    Args:
        log_dir: Directory for log files
        max_bytes: Maximum file size before rotation
        backup_count: Number of backup files to keep
        when: Time-based rotation (e.g., 'midnight', 'hourly')
        interval: Interval for time-based rotation
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Setup handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    handlers.append(console_handler)
    
    # File handler
    if when:
        # Time-based rotation
        file_handler = TimedRotatingFileHandler(
            filename=str(log_dir / "app.log"),
            when=when,
            interval=interval,
            backup_count=backup_count,
        )
    else:
        # Size-based rotation
        file_handler = RotatingFileHandler(
            filename=str(log_dir / "app.log"),
            max_bytes=max_bytes,
            backup_count=backup_count,
        )
    
    file_handler.setLevel(logging.DEBUG)
    handlers.append(file_handler)
    
    # Add handlers to root logger
    for handler in handlers:
        root_logger.addHandler(handler)
    
    root_logger.setLevel(logging.DEBUG)


def setup_log_aggregation(
    log_dir: Path,
    config: Optional[LogConfig] = None,
) -> None:
    """Setup comprehensive log aggregation with multiple specialized handlers.
    
    Args:
        log_dir: Directory for log files
        config: Logging configuration
    """
    if config is None:
        config = LogConfig()
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Setup specialized handlers
    handlers = []
    
    # Main application log
    if config.file and config.file.enabled:
        main_handler = RotatingFileHandler(
            filename=str(log_dir / "app.log"),
            max_bytes=config.file.max_bytes,
            backup_count=config.file.backup_count,
        )
        main_handler.setLevel(getattr(logging, config.file.level.value))
        handlers.append(main_handler)
    
    # Error log
    error_handler = setup_error_handler(log_dir)
    handlers.append(error_handler)
    
    # Performance log
    if config.performance.enabled:
        perf_handler = setup_performance_handler(log_dir)
        handlers.append(perf_handler)
    
    # Request log
    if config.request.enabled:
        request_handler = setup_request_handler(log_dir)
        handlers.append(request_handler)
    
    # Console handler
    if config.console.enabled:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config.console.level.value))
        handlers.append(console_handler)
    
    # Add all handlers to root logger
    for handler in handlers:
        root_logger.addHandler(handler)
    
    root_logger.setLevel(logging.DEBUG)


def setup_performance_monitoring(
    config: Optional[PerformanceConfig] = None,
    log_dir: Optional[Path] = None,
) -> None:
    """Setup performance monitoring with optional file logging.
    
    Args:
        config: Performance configuration
        log_dir: Directory for performance logs
    """
    if config is None:
        config = PerformanceConfig()
    
    # Setup performance logging
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        perf_logger = logging.getLogger("performance")
        
        # Add file handler for performance logs
        perf_handler = setup_performance_handler(log_dir)
        perf_logger.addHandler(perf_handler)
        perf_logger.setLevel(logging.INFO)
    
    # Initialize performance tracker
    setup_performance_logging(config=config)


def setup_environment_logging() -> None:
    """Setup logging based on environment variables."""
    log_level = os.getenv("BEACON_LOG_LEVEL", "INFO")
    log_format = os.getenv("BEACON_LOG_FORMAT", "text")
    log_dir = os.getenv("BEACON_LOG_DIR")
    
    # Configure basic logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Setup file logging if directory specified
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Add file handler
        file_handler = RotatingFileHandler(
            filename=str(log_path / "app.log"),
            max_bytes=10 * 1024 * 1024,  # 10MB
            backup_count=5,
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Get root logger and add handler
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)


def setup_development_logging() -> None:
    """Setup logging optimized for development."""
    # Configure for development with more verbose output
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def setup_production_logging(
    log_dir: Path,
    log_level: str = "INFO",
    log_format: str = "json",
) -> None:
    """Setup logging optimized for production.
    
    Args:
        log_dir: Directory for log files
        log_level: Log level
        log_format: Log format (text, json, structured)
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure for production with structured logging
    config = LogConfig(
        level=log_level,
        format=log_format,
        console=LogConfig.model_fields["console"].default,
        file=LogConfig.model_fields["file"].default,
    )
    config.file.directory = log_dir
    config.file.enabled = True
    
    setup_log_aggregation(log_dir, config)


class LogManager:
    """Manages multiple loggers and their configurations."""
    
    def __init__(self):
        self.loggers: Dict[str, logging.Logger] = {}
        self.configs: Dict[str, LogConfig] = {}
        self._lock = threading.Lock()
    
    def get_logger(
        self,
        name: str,
        config: Optional[LogConfig] = None,
    ) -> logging.Logger:
        """Get or create a logger with configuration.
        
        Args:
            name: Logger name
            config: Logger configuration
            
        Returns:
            Configured logger instance
        """
        with self._lock:
            if name in self.loggers:
                return self.loggers[name]
            
            # Create new logger
            logger = logging.getLogger(name)
            
            if config:
                self.configs[name] = config
                # Apply configuration
                self._apply_config(logger, config)
            
            self.loggers[name] = logger
            return logger
    
    def _apply_config(self, logger: logging.Logger, config: LogConfig) -> None:
        """Apply configuration to a logger.
        
        Args:
            logger: Logger instance
            config: Configuration to apply
        """
        # Clear existing handlers
        logger.handlers.clear()
        
        # Set level
        logger.setLevel(getattr(logging, config.level.value))
        
        # Set propagation
        logger.propagate = config.propagate
        
        # Note: Handler setup would be done here based on config
        # This is a simplified version
    
    def remove_logger(self, name: str) -> None:
        """Remove a logger from management.
        
        Args:
            name: Logger name
        """
        with self._lock:
            if name in self.loggers:
                del self.loggers[name]
            if name in self.configs:
                del self.configs[name]
    
    def get_all_loggers(self) -> Dict[str, logging.Logger]:
        """Get all managed loggers.
        
        Returns:
            Dictionary of logger names to logger instances
        """
        with self._lock:
            return self.loggers.copy()
    
    def clear_all_loggers(self) -> None:
        """Clear all managed loggers."""
        with self._lock:
            self.loggers.clear()
            self.configs.clear()


# Global log manager instance
_log_manager = LogManager()


def get_log_manager() -> LogManager:
    """Get the global log manager instance.
    
    Returns:
        Global log manager instance
    """
    return _log_manager
