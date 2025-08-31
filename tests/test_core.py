"""
Tests for core logging functionality.
"""

import logging
import tempfile
from pathlib import Path
import pytest

from beacon.core import setup_logger, get_logger, setup_structured_logging, get_structured_logger
from beacon.config import LogConfig, LogLevel, LogFormat


class TestCoreLogging:
    """Test core logging functionality."""
    
    def test_setup_logger_basic(self):
        """Test basic logger setup."""
        logger = setup_logger("test_logger")
        
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0
    
    def test_setup_logger_with_file(self):
        """Test logger setup with file output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir)
            logger = setup_logger("test_logger", log_dir=log_dir)
            
            assert logger.name == "test_logger"
            assert len(logger.handlers) > 0
            
            # Check that log file was created
            log_file = log_dir / "test_logger.log"
            assert log_file.exists()
    
    def test_setup_logger_debug(self):
        """Test logger setup with debug level."""
        logger = setup_logger("test_logger", debug=True)
        
        assert logger.level == logging.DEBUG
    
    def test_setup_logger_with_config(self):
        """Test logger setup with configuration."""
        config = LogConfig(
            level=LogLevel.DEBUG,
            format=LogFormat.JSON,
        )
        
        logger = setup_logger("test_logger", config=config)
        
        assert logger.level == logging.DEBUG
    
    def test_get_logger(self):
        """Test getting logger instance."""
        logger = get_logger("test_get_logger")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_get_logger"
    
    def test_get_logger_none(self):
        """Test getting root logger."""
        logger = get_logger()
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "root"
    
    def test_setup_structured_logging(self):
        """Test structured logging setup."""
        setup_structured_logging()
        
        # Should not raise any exceptions
        assert True
    
    def test_get_structured_logger(self):
        """Test getting structured logger."""
        setup_structured_logging()
        logger = get_structured_logger("test_structured")
        
        # Should be a structlog logger
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")


class TestLogConfig:
    """Test logging configuration."""
    
    def test_log_config_defaults(self):
        """Test default configuration values."""
        config = LogConfig()
        
        assert config.level == LogLevel.INFO
        assert config.format == LogFormat.TEXT
        assert config.console.enabled is True
        assert config.file is None
    
    def test_log_config_custom(self):
        """Test custom configuration."""
        config = LogConfig(
            level=LogLevel.DEBUG,
            format=LogFormat.JSON,
            name="custom_logger",
        )
        
        assert config.level == LogLevel.DEBUG
        assert config.format == LogFormat.JSON
        assert config.name == "custom_logger"
    
    def test_log_config_validation(self):
        """Test configuration validation."""
        # Should not raise exceptions for valid config
        config = LogConfig(
            level="DEBUG",
            format="json",
        )
        
        assert config.level == LogLevel.DEBUG
        assert config.format == LogFormat.JSON
