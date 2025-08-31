"""
Tests for performance logging functionality.
"""

import time
import pytest
from datetime import datetime, UTC

from beacon.performance import (
    PerformanceTracker,
    PerformanceMetric,
    log_performance,
    performance_tracker,
    get_performance_tracker,
)


class TestPerformanceMetric:
    """Test performance metric data structure."""

    def test_performance_metric_creation(self):
        """Test creating a performance metric."""
        metric = PerformanceMetric(
            operation="test_operation",
            duration=1.5,
            timestamp=datetime.now(UTC),
            context={"key": "value"},
        )

        assert metric.operation == "test_operation"
        assert metric.duration == 1.5
        assert metric.duration_ms == 1500.0
        assert metric.context["key"] == "value"

    def test_performance_metric_duration_ms(self):
        """Test duration in milliseconds calculation."""
        metric = PerformanceMetric(
            operation="test",
            duration=0.5,
            timestamp=datetime.now(UTC),
        )

        assert metric.duration_ms == 500.0


class TestPerformanceTracker:
    """Test performance tracker functionality."""

    def test_performance_tracker_creation(self):
        """Test creating a performance tracker."""
        tracker = PerformanceTracker()

        assert tracker.logger is not None
        assert tracker.config is not None
        assert len(tracker._metrics) == 0

    def test_log_performance(self):
        """Test logging performance metrics."""
        tracker = PerformanceTracker()

        tracker.log_performance(
            operation="test_operation",
            duration=1.0,
            context={"test": "data"},
            user_id="user123",
        )

        assert len(tracker._metrics) == 1
        metric = tracker._metrics[0]
        assert metric.operation == "test_operation"
        assert metric.duration == 1.0
        assert metric.context["test"] == "data"
        assert metric.user_id == "user123"

    def test_performance_tracker_context_manager(self):
        """Test performance tracker as context manager."""
        tracker = PerformanceTracker()

        with tracker.track_operation("test_operation", {"key": "value"}):
            time.sleep(0.1)  # Simulate some work

        assert len(tracker._metrics) == 1
        metric = tracker._metrics[0]
        assert metric.operation == "test_operation"
        assert metric.context["key"] == "value"
        assert metric.duration > 0

    def test_get_metrics(self):
        """Test getting metrics with filters."""
        tracker = PerformanceTracker()

        # Add some test metrics
        tracker.log_performance("op1", 1.0)
        tracker.log_performance("op2", 2.0)
        tracker.log_performance("op1", 1.5)

        # Test filtering by operation
        op1_metrics = tracker.get_metrics(operation="op1")
        assert len(op1_metrics) == 2

        # Test limiting results
        limited_metrics = tracker.get_metrics(limit=2)
        assert len(limited_metrics) == 2

    def test_get_statistics(self):
        """Test getting performance statistics."""
        tracker = PerformanceTracker()

        # Add test metrics
        tracker.log_performance("test_op", 1.0)
        tracker.log_performance("test_op", 2.0)
        tracker.log_performance("test_op", 3.0)

        stats = tracker.get_statistics(operation="test_op")

        assert stats["count"] == 3
        assert stats["total_duration"] == 6.0
        assert stats["avg_duration"] == 2.0
        assert stats["min_duration"] == 1.0
        assert stats["max_duration"] == 3.0

    def test_clear_metrics(self):
        """Test clearing metrics."""
        tracker = PerformanceTracker()

        tracker.log_performance("test_op", 1.0)
        assert len(tracker._metrics) == 1

        tracker.clear_metrics()
        assert len(tracker._metrics) == 0


class TestPerformanceFunctions:
    """Test performance utility functions."""

    def setup_method(self):
        """Clear metrics before each test."""
        tracker = get_performance_tracker()
        tracker.clear_metrics()

    def test_log_performance_function(self):
        """Test the log_performance utility function."""
        log_performance("test_op", 1.5, {"key": "value"})

        tracker = get_performance_tracker()
        assert len(tracker._metrics) == 1
        metric = tracker._metrics[0]
        assert metric.operation == "test_op"
        assert metric.duration == 1.5

    def test_performance_tracker_context_manager_function(self):
        """Test the performance_tracker context manager function."""
        with performance_tracker("test_op", {"key": "value"}):
            time.sleep(0.1)

        tracker = get_performance_tracker()
        assert len(tracker._metrics) == 1
        metric = tracker._metrics[0]
        assert metric.operation == "test_op"
        assert metric.context["key"] == "value"

    def test_get_performance_tracker_singleton(self):
        """Test that get_performance_tracker returns the same instance."""
        tracker1 = get_performance_tracker()
        tracker2 = get_performance_tracker()

        assert tracker1 is tracker2
