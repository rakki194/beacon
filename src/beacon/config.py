"""
Configuration classes and enums for Beacon logging framework.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    """Log levels supported by Beacon."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Log output formats supported by Beacon."""

    TEXT = "text"
    JSON = "json"
    STRUCTURED = "structured"


@dataclass
class HandlerConfig:
    """Configuration for a log handler."""

    enabled: bool = True
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.TEXT
    max_bytes: Optional[int] = None
    backup_count: Optional[int] = None
    when: Optional[str] = None
    interval: Optional[int] = None


@dataclass
class FileHandlerConfig(HandlerConfig):
    """Configuration for file-based log handlers."""

    filename: Optional[Path] = None
    directory: Optional[Path] = None
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class ConsoleHandlerConfig(HandlerConfig):
    """Configuration for console log handlers."""

    stream: str = "stdout"  # "stdout" or "stderr"


@dataclass
class PerformanceConfig:
    """Configuration for performance logging."""

    enabled: bool = True
    track_memory: bool = True
    track_cpu: bool = True
    track_disk: bool = False
    track_network: bool = False
    interval_seconds: float = 60.0
    threshold_ms: float = 1000.0  # Log operations slower than this


@dataclass
class RequestLoggingConfig:
    """Configuration for request logging."""

    enabled: bool = True
    log_headers: bool = False
    log_body: bool = False
    log_query_params: bool = True
    log_response_time: bool = True
    log_status_codes: bool = True
    sensitive_headers: List[str] = field(
        default_factory=lambda: ["authorization", "cookie"]
    )


@dataclass
class TrainingLoggingConfig:
    """Configuration for training event logging."""

    enabled: bool = True
    log_metrics: bool = True
    log_checkpoints: bool = True
    log_validation: bool = True
    log_hyperparameters: bool = True


class LogConfig(BaseModel):
    """Main configuration class for Beacon logging."""

    # Basic configuration
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.TEXT
    name: Optional[str] = None

    # Handler configurations
    console: ConsoleHandlerConfig = Field(default_factory=ConsoleHandlerConfig)
    file: Optional[FileHandlerConfig] = None

    # Performance monitoring
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)

    # Request logging
    request: RequestLoggingConfig = Field(default_factory=RequestLoggingConfig)

    # Training logging
    training: TrainingLoggingConfig = Field(default_factory=TrainingLoggingConfig)

    # Advanced options
    propagate: bool = False
    disable_existing_loggers: bool = False
    include_timestamp: bool = True
    include_logger_name: bool = True
    include_module: bool = False
    include_function: bool = False
    include_line_number: bool = False

    # Context tracking
    track_user_id: bool = False
    track_session_id: bool = False
    track_request_id: bool = False

    # Custom fields
    extra_fields: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"use_enum_values": True, "validate_assignment": True}
