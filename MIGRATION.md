# Migration Guide

This guide helps you migrate from existing logging solutions to the Beacon library.

## From `utils/lib/logging_utils.py`

### Before (Old Code)

```python
from utils.lib.logging_utils import setup_logger

logger = setup_logger("my_app", log_dir="/var/log", debug=True)
```

### After (Beacon)

```python
from beacon import setup_logger
from pathlib import Path

logger = setup_logger("my_app", log_dir=Path("/var/log"), debug=True)
```

## From `games/mlgame/backend/app/utils/logging.py`

### Before (Old Code)

```python
from games.mlgame.backend.app.utils.logging import (
    setup_logging,
    get_logger,
    log_request_info,
    log_training_event,
    log_model_event
)

setup_logging()
logger = get_logger("my_app")

log_request_info(logger, {
    "method": "GET",
    "path": "/api/users",
    "status_code": 200,
    "duration": 0.15
})

log_training_event(logger, "session_123", "training_start")
log_model_event(logger, 1, "model_saved")
```

### After (Beacon)

```python
from beacon import (
    setup_structured_logging,
    get_structured_logger,
    RequestLogger,
    TrainingLogger
)

# Setup structured logging
setup_structured_logging()

# Get structured logger
logger = get_structured_logger("my_app")

# Request logging
request_logger = RequestLogger()
request_logger.log_request(
    method="GET",
    path="/api/users",
    status_code=200,
    duration=0.15
)

# Training logging
training_logger = TrainingLogger()
training_logger.log_training_event("session_123", "training_start")
training_logger.log_model_event(1, "model_saved")
```

## From PawPrint Logging Manager

### Before (Old Code)

```python
from pawprint.core.logging_manager import LoggingManager

logging_manager = LoggingManager()
with logging_manager.performance_tracker("operation", {"context": "data"}):
    # Your operation here
    pass
```

### After (Beacon)

```python
from beacon import performance_tracker

with performance_tracker("operation", {"context": "data"}):
    # Your operation here
    pass
```

## Environment Variables

### Before

```bash
# Various environment variables for different logging systems
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_DIR=/var/log
```

### After

```bash
# Beacon environment variables
BEACON_LOG_LEVEL=INFO
BEACON_LOG_FORMAT=json
BEACON_LOG_DIR=/var/log
BEACON_LOG_NAME=my_app
```

## Configuration Migration

### Before (Custom Config)

```python
# Custom configuration object
config = {
    "level": "DEBUG",
    "format": "json",
    "handlers": ["console", "file"],
    "log_dir": "/var/log"
}
```

### After (Beacon Config)

```python
from beacon import LogConfig, LogLevel, LogFormat, FileHandlerConfig
from pathlib import Path

config = LogConfig(
    level=LogLevel.DEBUG,
    format=LogFormat.JSON,
    file=FileHandlerConfig(
        directory=Path("/var/log"),
        enabled=True
    )
)
```

## Performance Monitoring Migration

### Before (Custom Performance Tracking)

```python
import time

start_time = time.time()
# Your operation
duration = time.time() - start_time
logger.info(f"Operation took {duration:.3f}s")
```

### After (Beacon Performance Tracking)

```python
from beacon import performance_tracker

with performance_tracker("operation_name", {"context": "data"}):
    # Your operation
    pass
```

## Request Logging Migration

### Before (Custom Request Logging)

```python
def log_request(request, response, duration):
    logger.info(f"{request.method} {request.path} - {response.status_code} ({duration:.3f}s)")
```

### After (Beacon Request Logging)

```python
from beacon import RequestLogger

request_logger = RequestLogger()

def log_request(request, response, duration):
    request_logger.log_request(
        method=request.method,
        path=request.path,
        status_code=response.status_code,
        duration=duration,
        user_agent=request.headers.get("User-Agent"),
        ip_address=request.remote_addr
    )
```

## Training Logging Migration

### Before (Custom Training Logging)

```python
def log_training_step(step, epoch, loss):
    logger.info(f"Step {step}, Epoch {epoch}, Loss: {loss}")
```

### After (Beacon Training Logging)

```python
from beacon import TrainingLogger

training_logger = TrainingLogger()

def log_training_step(step, epoch, loss):
    training_logger.log_training_step(
        session_id="train_001",
        step=step,
        epoch=epoch,
        loss=loss
    )
```

## Benefits of Migration

1. **Unified API**: Single, consistent logging interface across all projects
2. **Better Performance**: Built-in performance monitoring and metrics collection
3. **Structured Logging**: JSON and structured log formats for better parsing
4. **Type Safety**: Full type hints and Pydantic validation
5. **Flexible Configuration**: Environment variables, configuration objects, and more
6. **Log Aggregation**: Automatic log rotation and specialized handlers
7. **Request Tracking**: Built-in HTTP request/response logging
8. **Training Support**: Specialized ML training event logging

## Testing Migration

After migrating, test your logging setup:

```python
from beacon import setup_logger, performance_tracker

# Test basic logging
logger = setup_logger("test_app")
logger.info("Migration successful!")

# Test performance tracking
with performance_tracker("test_operation"):
    import time
    time.sleep(0.1)

print("✅ Migration test completed!")
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure beacon is installed: `pip install beacon`
2. **Configuration Errors**: Check that LogConfig values are valid
3. **Handler Issues**: Verify that log directories exist and are writable
4. **Performance Issues**: Ensure performance tracking is properly configured

### Getting Help

- Check the [README.md](README.md) for detailed documentation
- Run the [examples/basic_usage.py](examples/basic_usage.py) to see working examples
- Review the test files in [tests/](tests/) for usage patterns
