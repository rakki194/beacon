#!/usr/bin/env python3
"""
Basic usage example for Beacon logging framework.

This example demonstrates the core features of Beacon including:
- Basic logging setup
- Structured logging
- Performance monitoring
- Request logging
- Training logging
"""

import time
import tempfile
from pathlib import Path

# Import beacon components
from beacon import (
    setup_logger,
    setup_structured_logging,
    get_structured_logger,
    performance_tracker,
    log_performance,
    RequestLogger,
    TrainingLogger,
    LogConfig,
    LogLevel,
    LogFormat,
)


def basic_logging_example():
    """Demonstrate basic logging functionality."""
    print("=== Basic Logging Example ===")
    
    # Setup a basic logger
    logger = setup_logger("basic_example")
    
    # Log different levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Log with extra context
    logger.info("User action", extra={
        "user_id": "123",
        "action": "login",
        "ip_address": "192.168.1.1"
    })


def structured_logging_example():
    """Demonstrate structured logging functionality."""
    print("\n=== Structured Logging Example ===")
    
    # Setup structured logging
    setup_structured_logging()
    
    # Get a structured logger
    logger = get_structured_logger("structured_example")
    
    # Log with structured data
    logger.info("User logged in", 
                user_id="123", 
                action="login", 
                ip_address="192.168.1.1",
                timestamp="2024-01-01T12:00:00Z")
    
    logger.error("Database connection failed",
                error_code=500,
                database="postgres",
                retry_count=3)


def performance_monitoring_example():
    """Demonstrate performance monitoring functionality."""
    print("\n=== Performance Monitoring Example ===")
    
    # Track performance with context manager
    with performance_tracker("database_query", {"table": "users", "operation": "select"}):
        # Simulate database query
        time.sleep(0.1)
        print("  Executed database query")
    
    # Track performance with context manager and additional context
    with performance_tracker("api_call", {"endpoint": "/api/users", "method": "GET"}):
        # Simulate API call
        time.sleep(0.05)
        print("  Made API call")
    
    # Log performance manually
    log_performance("file_operation", 0.025, {"file": "data.csv", "operation": "read"})


def request_logging_example():
    """Demonstrate request logging functionality."""
    print("\n=== Request Logging Example ===")
    
    # Create a request logger
    request_logger = RequestLogger()
    
    # Simulate HTTP requests
    requests = [
        {
            "method": "GET",
            "path": "/api/users",
            "status_code": 200,
            "duration": 0.15,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "ip_address": "192.168.1.1",
            "user_id": "123"
        },
        {
            "method": "POST",
            "path": "/api/users",
            "status_code": 201,
            "duration": 0.25,
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "ip_address": "192.168.1.2",
            "user_id": "456"
        },
        {
            "method": "GET",
            "path": "/api/users/999",
            "status_code": 404,
            "duration": 0.05,
            "user_agent": "curl/7.68.0",
            "ip_address": "192.168.1.3",
            "user_id": None
        }
    ]
    
    for request in requests:
        request_logger.log_request(**request)
        print(f"  Logged {request['method']} {request['path']} - {request['status_code']}")


def training_logging_example():
    """Demonstrate training logging functionality."""
    print("\n=== Training Logging Example ===")
    
    # Create a training logger
    training_logger = TrainingLogger()
    
    session_id = "train_001"
    
    # Log training start
    training_logger.log_training_start(
        session_id=session_id,
        model_name="bert-base-uncased",
        hyperparameters={
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 10,
            "optimizer": "adam"
        },
        dataset_info={
            "name": "imdb",
            "size": 25000,
            "split": "train"
        }
    )
    
    # Simulate training steps
    for epoch in range(3):
        for step in range(0, 100, 25):
            # Simulate training step
            loss = 1.0 - (epoch * 0.3 + step * 0.002)
            accuracy = 0.5 + (epoch * 0.15 + step * 0.001)
            
            training_logger.log_training_step(
                session_id=session_id,
                step=step,
                epoch=epoch,
                loss=loss,
                metrics={
                    "accuracy": accuracy,
                    "learning_rate": 0.001
                }
            )
        
        # Log validation
        training_logger.log_validation(
            session_id=session_id,
            epoch=epoch,
            validation_loss=loss * 0.9,
            validation_metrics={
                "accuracy": accuracy * 0.95,
                "f1_score": accuracy * 0.92
            }
        )
        
        # Log checkpoint
        training_logger.log_checkpoint(
            session_id=session_id,
            checkpoint_path=f"/checkpoints/model_epoch_{epoch}.pt",
            epoch=epoch,
            metrics={
                "loss": loss,
                "accuracy": accuracy
            }
        )
    
    # Log training end
    training_logger.log_training_end(
        session_id=session_id,
        final_metrics={
            "final_loss": 0.1,
            "final_accuracy": 0.95,
            "training_time": 3600  # 1 hour
        },
        training_time=3600
    )


def file_logging_example():
    """Demonstrate file logging functionality."""
    print("\n=== File Logging Example ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir)
        
        # Setup logger with file output
        logger = setup_logger("file_example", log_dir=log_dir)
        
        # Log some messages
        logger.info("This message will be written to a file")
        logger.warning("This warning will also be in the file")
        logger.error("This error will be in the file too")
        
        # Check that log file was created
        log_file = log_dir / "file_example.log"
        if log_file.exists():
            print(f"  Log file created: {log_file}")
            print(f"  File size: {log_file.stat().st_size} bytes")
        else:
            print("  Log file was not created")


def configuration_example():
    """Demonstrate configuration functionality."""
    print("\n=== Configuration Example ===")
    
    # Create custom configuration
    config = LogConfig(
        level=LogLevel.DEBUG,
        format=LogFormat.JSON,
        name="config_example",
        console=LogConfig.model_fields["console"].default,
    )
    config.console.enabled = True
    config.console.level = LogLevel.DEBUG
    
    # Setup logger with custom configuration
    logger = setup_logger("config_example", config=config)
    
    # Log with the configured logger
    logger.debug("Debug message with custom config")
    logger.info("Info message with custom config", extra={"config": "custom"})


def main():
    """Run all examples."""
    print("Beacon Logging Framework - Basic Usage Examples")
    print("=" * 50)
    
    try:
        basic_logging_example()
        structured_logging_example()
        performance_monitoring_example()
        request_logging_example()
        training_logging_example()
        file_logging_example()
        configuration_example()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
