"""
Beacon - A comprehensive logging framework for Python applications.

Beacon provides structured logging, performance monitoring, and log aggregation
capabilities for modern Python applications.
"""

from .core import (
    setup_logger,
    get_logger,
    setup_structured_logging,
    get_structured_logger,
)
from .formatters import StructuredFormatter, JSONFormatter
from .handlers import (
    RotatingFileHandler,
    TimedRotatingFileHandler,
    setup_handlers,
)
from .performance import (
    PerformanceTracker,
    log_performance,
    performance_tracker,
)
from .request import (
    RequestLogger,
    log_request_info,
    setup_request_logging,
)
from .training import (
    TrainingLogger,
    log_training_event,
    log_model_event,
)
from .config import LogConfig, LogLevel, LogFormat
from .utils import (
    setup_log_rotation,
    setup_log_aggregation,
    setup_performance_monitoring,
)

__version__ = "0.1.0"
__author__ = "Runeset Team"
__email__ = "team@runeset.dev"

__all__ = [
    # Core logging
    "setup_logger",
    "get_logger",
    "setup_structured_logging",
    "get_structured_logger",
    
    # Formatters
    "StructuredFormatter",
    "JSONFormatter",
    
    # Handlers
    "RotatingFileHandler",
    "TimedRotatingFileHandler",
    "setup_handlers",
    
    # Performance
    "PerformanceTracker",
    "log_performance",
    "performance_tracker",
    
    # Request logging
    "RequestLogger",
    "log_request_info",
    "setup_request_logging",
    
    # Training logging
    "TrainingLogger",
    "log_training_event",
    "log_model_event",
    
    # Configuration
    "LogConfig",
    "LogLevel",
    "LogFormat",
    
    # Utilities
    "setup_log_rotation",
    "setup_log_aggregation",
    "setup_performance_monitoring",
]
