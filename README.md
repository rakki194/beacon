# Beacon

A comprehensive logging framework for Python applications that provides structured logging, performance monitoring, and log aggregation capabilities.

## Features

- **Structured Logging**: JSON and structured log formats with context support
- **Performance Monitoring**: Built-in performance tracking and metrics collection
- **Request Logging**: Specialized HTTP request logging with middleware support
- **Training Logging**: ML training event logging with session tracking
- **Log Rotation**: Automatic log file rotation and management
- **Multiple Handlers**: Console, file, and specialized handlers (errors, performance, requests)
- **Configuration**: Flexible configuration system with environment variable support
- **Type Safety**: Full type hints and Pydantic validation

## Installation

```bash
pip install beacon
```

For development dependencies:

```bash
pip install beacon[dev]
```

For performance monitoring:

```bash
pip install beacon[performance]
```

## Quick Start

### Basic Usage

```python
from beacon import setup_logger, get_logger

# Setup a logger
logger = setup_logger("my_app")

# Use the logger
logger.info("Application started")
logger.error("An error occurred", extra={"error_code": 500})
```

### Structured Logging

```python
from beacon import setup_structured_logging, get_structured_logger

# Setup structured logging
setup_structured_logging()

# Get a structured logger
logger = get_structured_logger("my_app")

# Log with structured data
logger.info("User action", user_id="123", action="login", ip="192.168.1.1")
```

### Performance Monitoring

```python
from beacon import performance_tracker, log_performance

# Track performance with context manager
with performance_tracker("database_query", {"table": "users"}):
    # Your database operation here
    result = db.query("SELECT * FROM users")

# Or log performance manually
log_performance("api_call", 1.5, {"endpoint": "/api/users"})
```

### Request Logging

```python
from beacon import RequestLogger

# Create a request logger
request_logger = RequestLogger()

# Log HTTP requests
request_logger.log_request(
    method="GET",
    path="/api/users",
    status_code=200,
    duration=0.15,
    user_agent="Mozilla/5.0...",
    ip_address="192.168.1.1",
    user_id="123"
)
```

### Training Logging

```python
from beacon import TrainingLogger

# Create a training logger
training_logger = TrainingLogger()

# Log training events
training_logger.log_training_start(
    session_id="train_001",
    model_name="bert-base",
    hyperparameters={"lr": 0.001, "batch_size": 32}
)

training_logger.log_training_step(
    session_id="train_001",
    step=100,
    epoch=1,
    loss=0.5,
    metrics={"accuracy": 0.85}
)
```

## Configuration

### Basic Configuration

```python
from beacon import LogConfig, setup_logger

config = LogConfig(
    level="DEBUG",
    format="json",
    name="my_app"
)

logger = setup_logger("my_app", config=config)
```

### File Logging

```python
from pathlib import Path
from beacon import LogConfig, FileHandlerConfig

config = LogConfig(
    file=FileHandlerConfig(
        directory=Path("/var/log/my_app"),
        max_bytes=10 * 1024 * 1024,  # 10MB
        backup_count=5
    )
)

logger = setup_logger("my_app", config=config)
```

### Environment Variables

```bash
export BEACON_LOG_LEVEL=DEBUG
export BEACON_LOG_FORMAT=json
export BEACON_LOG_DIR=/var/log/my_app
```

Then use:

```python
from beacon import setup_logging_from_env

logger = setup_logging_from_env()
```

## Advanced Usage

### Custom Formatters

```python
from beacon import StructuredFormatter, setup_logger
import logging

# Create custom formatter
formatter = StructuredFormatter(include_context=True)

# Setup logger with custom formatter
logger = setup_logger("my_app")
for handler in logger.handlers:
    handler.setFormatter(formatter)
```

### Log Aggregation

```python
from pathlib import Path
from beacon import setup_log_aggregation

# Setup comprehensive log aggregation
setup_log_aggregation(
    log_dir=Path("/var/log/my_app"),
    config=LogConfig(
        performance=PerformanceConfig(enabled=True),
        request=RequestLoggingConfig(enabled=True)
    )
)
```

### Performance Monitoring

```python
from beacon import setup_performance_monitoring, PerformanceConfig

# Setup performance monitoring
config = PerformanceConfig(
    track_memory=True,
    track_cpu=True,
    threshold_ms=1000  # Log operations slower than 1 second
)

setup_performance_monitoring(config=config)
```

### Request Middleware

```python
from beacon import create_request_middleware

# Create middleware for your web framework
middleware = create_request_middleware()

# Use in your request processing
def handle_request(request, response):
    start_time = time.time()
    # Process request
    duration = time.time() - start_time
    middleware(request, response, duration)
```

## API Reference

### Core Functions

- `setup_logger(name, log_dir=None, debug=False, config=None)` - Setup a logger
- `get_logger(name=None)` - Get a logger instance
- `setup_structured_logging(config=None, log_level=None, log_format=None)` - Setup structured logging
- `get_structured_logger(name=None)` - Get a structured logger

### Performance Functions

- `log_performance(operation, duration, context=None, **kwargs)` - Log performance metric
- `performance_tracker(operation, context=None, **kwargs)` - Context manager for performance tracking
- `get_performance_tracker()` - Get global performance tracker

### Request Functions

- `log_request_info(logger, request_info)` - Log request information
- `setup_request_logging(logger=None, config=None)` - Setup request logging

### Training Functions

- `log_training_event(logger, session_id, event_type, **kwargs)` - Log training event
- `log_model_event(logger, model_id, event_type, **kwargs)` - Log model event
- `setup_training_logging(logger=None, config=None)` - Setup training logging

### Utility Functions

- `setup_log_rotation(log_dir, max_bytes, backup_count, when, interval)` - Setup log rotation
- `setup_log_aggregation(log_dir, config=None)` - Setup comprehensive log aggregation
- `setup_performance_monitoring(config=None, log_dir=None)` - Setup performance monitoring
- `setup_environment_logging()` - Setup logging from environment variables
- `setup_development_logging()` - Setup development-optimized logging
- `setup_production_logging(log_dir, log_level, log_format)` - Setup production logging

## Configuration Classes

### LogConfig

Main configuration class with the following fields:

- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `format`: Log format (text, json, structured)
- `name`: Logger name
- `console`: Console handler configuration
- `file`: File handler configuration
- `performance`: Performance monitoring configuration
- `request`: Request logging configuration
- `training`: Training logging configuration

### HandlerConfig

Base configuration for log handlers:

- `enabled`: Whether the handler is enabled
- `level`: Handler log level
- `format`: Handler log format
- `max_bytes`: Maximum file size for rotation
- `backup_count`: Number of backup files to keep

### PerformanceConfig

Performance monitoring configuration:

- `enabled`: Whether performance monitoring is enabled
- `track_memory`: Whether to track memory usage
- `track_cpu`: Whether to track CPU usage
- `threshold_ms`: Threshold for logging slow operations
- `interval_seconds`: Monitoring interval

### RequestLoggingConfig

Request logging configuration:

- `enabled`: Whether request logging is enabled
- `log_headers`: Whether to log request headers
- `log_body`: Whether to log request body
- `log_query_params`: Whether to log query parameters
- `sensitive_headers`: List of sensitive headers to filter

### TrainingLoggingConfig

Training logging configuration:

- `enabled`: Whether training logging is enabled
- `log_metrics`: Whether to log training metrics
- `log_checkpoints`: Whether to log checkpoints
- `log_validation`: Whether to log validation results
- `log_hyperparameters`: Whether to log hyperparameters

## Examples

### Web Application

```python
from beacon import setup_logger, RequestLogger, performance_tracker
from flask import Flask, request, g
import time

app = Flask(__name__)

# Setup logging
logger = setup_logger("web_app")
request_logger = RequestLogger()

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    
    request_logger.log_request(
        method=request.method,
        path=request.path,
        status_code=response.status_code,
        duration=duration,
        user_agent=request.headers.get("User-Agent"),
        ip_address=request.remote_addr
    )
    
    return response

@app.route("/api/users")
@performance_tracker("get_users")
def get_users():
    # Your API logic here
    return {"users": []}
```

### Machine Learning Training

```python
from beacon import TrainingLogger, performance_tracker
import torch

# Setup training logger
training_logger = TrainingLogger()

def train_model(model, dataloader, epochs):
    session_id = "train_001"
    
    training_logger.log_training_start(
        session_id=session_id,
        model_name="bert-base",
        hyperparameters={"lr": 0.001, "batch_size": 32}
    )
    
    for epoch in range(epochs):
        for batch_idx, (data, target) in enumerate(dataloader):
            with performance_tracker("training_step"):
                # Training step
                loss = model(data, target)
                
                if batch_idx % 100 == 0:
                    training_logger.log_training_step(
                        session_id=session_id,
                        step=batch_idx,
                        epoch=epoch,
                        loss=loss.item()
                    )
    
    training_logger.log_training_end(
        session_id=session_id,
        training_time=total_time
    )
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=beacon
```

### Code Formatting

```bash
# Format code
black src/beacon tests/

# Sort imports
isort src/beacon tests/
```

### Type Checking

```bash
# Run type checker
mypy src/beacon
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Changelog

### 0.1.0

- Initial release
- Core logging functionality
- Structured logging support
- Performance monitoring
- Request logging
- Training logging
- Log rotation and aggregation
- Configuration system
