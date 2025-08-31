"""
Custom formatters for Beacon logging framework.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class LogEntry:
    """Represents a structured log entry."""
    
    timestamp: datetime
    level: str
    logger_name: str
    message: str
    module: str
    function: str
    line_number: int
    exception_info: Optional[str] = None
    context: Dict[str, Any] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def __init__(self, include_context: bool = True, include_extra: bool = True):
        super().__init__()
        self.include_context = include_context
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = LogEntry(
            timestamp=datetime.fromtimestamp(record.created),
            level=record.levelname,
            logger_name=record.name,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line_number=record.lineno,
            exception_info=(
                self.formatException(record.exc_info) if record.exc_info else None
            ),
            context=getattr(record, "context", {}),
            user_id=getattr(record, "user_id", None),
            session_id=getattr(record, "session_id", None),
            request_id=getattr(record, "request_id", None),
        )
        
        # Add extra fields if requested
        if self.include_extra:
            for key, value in record.__dict__.items():
                if key not in [
                    "name", "msg", "args", "levelname", "levelno", "pathname",
                    "filename", "module", "lineno", "funcName", "created",
                    "msecs", "relativeCreated", "thread", "threadName",
                    "processName", "process", "getMessage", "exc_info",
                    "exc_text", "stack_info", "context", "user_id", "session_id",
                    "request_id"
                ]:
                    log_entry.context[key] = value
        
        return json.dumps(asdict(log_entry), default=str)


class JSONFormatter(logging.Formatter):
    """JSON formatter for logging records."""
    
    def __init__(self, include_extra: bool = True, flatten: bool = False):
        super().__init__()
        self.include_extra = include_extra
        self.flatten = flatten
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if self.include_extra:
            for key, value in record.__dict__.items():
                if key not in [
                    "name", "msg", "args", "levelname", "levelno", "pathname",
                    "filename", "module", "lineno", "funcName", "created",
                    "msecs", "relativeCreated", "thread", "threadName",
                    "processName", "process", "getMessage", "exc_info", "exc_text", "stack_info"
                ]:
                    if self.flatten:
                        log_data[key] = value
                    else:
                        if "extra" not in log_data:
                            log_data["extra"] = {}
                        log_data["extra"][key] = value
        
        return json.dumps(log_data, default=str)


class TextFormatter(logging.Formatter):
    """Enhanced text formatter with context support."""
    
    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        include_context: bool = True,
    ):
        if fmt is None:
            fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        super().__init__(fmt, datefmt)
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with optional context."""
        formatted = super().format(record)
        
        if self.include_context:
            context_parts = []
            
            # Add user context
            if hasattr(record, "user_id") and record.user_id:
                context_parts.append(f"user={record.user_id}")
            if hasattr(record, "session_id") and record.session_id:
                context_parts.append(f"session={record.session_id}")
            if hasattr(record, "request_id") and record.request_id:
                context_parts.append(f"request={record.request_id}")
            
            # Add custom context
            if hasattr(record, "context") and record.context:
                for key, value in record.context.items():
                    context_parts.append(f"{key}={value}")
            
            if context_parts:
                formatted += f" [{' '.join(context_parts)}]"
        
        return formatted


class ColoredFormatter(logging.Formatter):
    """Colored text formatter for console output."""
    
    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
        "RESET": "\033[0m",     # Reset
    }
    
    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        include_context: bool = True,
    ):
        if fmt is None:
            fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        super().__init__(fmt, datefmt)
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        # Add color to level name
        level_color = self.COLORS.get(record.levelname, "")
        reset_color = self.COLORS["RESET"]
        
        # Temporarily modify the record
        original_levelname = record.levelname
        record.levelname = f"{level_color}{record.levelname}{reset_color}"
        
        try:
            formatted = super().format(record)
            
            if self.include_context:
                context_parts = []
                
                # Add user context
                if hasattr(record, "user_id") and record.user_id:
                    context_parts.append(f"user={record.user_id}")
                if hasattr(record, "session_id") and record.session_id:
                    context_parts.append(f"session={record.session_id}")
                if hasattr(record, "request_id") and record.request_id:
                    context_parts.append(f"request={record.request_id}")
                
                # Add custom context
                if hasattr(record, "context") and record.context:
                    for key, value in record.context.items():
                        context_parts.append(f"{key}={value}")
                
                if context_parts:
                    formatted += f" [{' '.join(context_parts)}]"
            
            return formatted
        finally:
            # Restore original level name
            record.levelname = original_levelname
