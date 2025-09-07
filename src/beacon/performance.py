"""
Performance logging and monitoring utilities for Beacon.
"""

import logging
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Callable, Dict, List, Optional

import structlog

from .config import PerformanceConfig


@dataclass
class PerformanceMetric:
    """Represents a performance metric."""

    operation: str
    duration: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None

    @property
    def duration_ms(self) -> float:
        """Duration in milliseconds."""
        return self.duration * 1000


class PerformanceTracker:
    """Tracks and logs performance metrics."""

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        config: Optional[PerformanceConfig] = None,
    ):
        self.logger = logger or logging.getLogger("performance")
        self.config = config or PerformanceConfig()
        self._metrics: List[PerformanceMetric] = []
        self._lock = threading.Lock()

    def log_performance(
        self,
        operation: str,
        duration: float,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        """Log a performance metric.

        Args:
            operation: Name of the operation
            duration: Duration in seconds
            context: Additional context information
            user_id: User ID for tracking
            session_id: Session ID for tracking
            request_id: Request ID for tracking
        """
        metric = PerformanceMetric(
            operation=operation,
            duration=duration,
            timestamp=datetime.now(UTC),
            context=context or {},
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
        )

        # Check if we should log based on threshold
        if duration * 1000 >= self.config.threshold_ms:
            self._log_metric(metric)

        # Store metric for aggregation
        with self._lock:
            self._metrics.append(metric)

    def _log_metric(self, metric: PerformanceMetric) -> None:
        """Log a performance metric."""
        log_data = {
            "operation": metric.operation,
            "duration_ms": metric.duration_ms,
            "duration_seconds": metric.duration,
            "timestamp": metric.timestamp.isoformat(),
        }

        # Add context
        if metric.context:
            log_data.update(metric.context)

        # Add tracking information
        if metric.user_id:
            log_data["user_id"] = metric.user_id
        if metric.session_id:
            log_data["session_id"] = metric.session_id
        if metric.request_id:
            log_data["request_id"] = metric.request_id

        self.logger.info(
            f"Performance: {metric.operation} took {metric.duration:.3f}s",
            extra=log_data,
        )

    @contextmanager
    def track_operation(
        self,
        operation: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        """Context manager for tracking operation performance.

        Args:
            operation: Name of the operation
            context: Additional context information
            user_id: User ID for tracking
            session_id: Session ID for tracking
            request_id: Request ID for tracking
        """
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            duration = end_time - start_time
            self.log_performance(
                operation=operation,
                duration=duration,
                context=context,
                user_id=user_id,
                session_id=session_id,
                request_id=request_id,
            )

    def get_metrics(
        self,
        operation: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[PerformanceMetric]:
        """Get stored performance metrics.

        Args:
            operation: Filter by operation name
            since: Filter by timestamp
            limit: Maximum number of metrics to return

        Returns:
            List of performance metrics
        """
        with self._lock:
            metrics = self._metrics.copy()

        # Apply filters
        if operation:
            metrics = [m for m in metrics if m.operation == operation]

        if since:
            metrics = [m for m in metrics if m.timestamp >= since]

        # Apply limit
        if limit:
            metrics = metrics[-limit:]

        return metrics

    def get_statistics(
        self,
        operation: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get performance statistics.

        Args:
            operation: Filter by operation name
            since: Filter by timestamp

        Returns:
            Dictionary with performance statistics
        """
        metrics = self.get_metrics(operation=operation, since=since)

        if not metrics:
            return {
                "count": 0,
                "total_duration": 0.0,
                "avg_duration": 0.0,
                "min_duration": 0.0,
                "max_duration": 0.0,
                "p95_duration": 0.0,
                "p99_duration": 0.0,
            }

        durations = [m.duration for m in metrics]
        durations.sort()

        count = len(durations)
        total_duration = sum(durations)
        avg_duration = total_duration / count
        min_duration = durations[0]
        max_duration = durations[-1]

        # Calculate percentiles
        p95_index = int(count * 0.95)
        p99_index = int(count * 0.99)

        p95_duration = durations[p95_index] if p95_index < count else max_duration
        p99_duration = durations[p99_index] if p99_index < count else max_duration

        return {
            "count": count,
            "total_duration": total_duration,
            "avg_duration": avg_duration,
            "min_duration": min_duration,
            "max_duration": max_duration,
            "p95_duration": p95_duration,
            "p99_duration": p99_duration,
        }

    def clear_metrics(self) -> None:
        """Clear stored metrics."""
        with self._lock:
            self._metrics.clear()


# Global performance tracker instance
_global_tracker: Optional[PerformanceTracker] = None


def get_performance_tracker() -> PerformanceTracker:
    """Get the global performance tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = PerformanceTracker()
    return _global_tracker


def log_performance(
    operation: str,
    duration: float,
    context: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> None:
    """Log a performance metric using the global tracker.

    Args:
        operation: Name of the operation
        duration: Duration in seconds
        context: Additional context information
        **kwargs: Additional tracking parameters (user_id, session_id, request_id)
    """
    tracker = get_performance_tracker()
    tracker.log_performance(operation, duration, context, **kwargs)


@contextmanager
def performance_tracker(
    operation: str,
    context: Optional[Dict[str, Any]] = None,
    **kwargs,
):
    """Context manager for tracking operation performance using the global tracker.

    Args:
        operation: Name of the operation
        context: Additional context information
        **kwargs: Additional tracking parameters (user_id, session_id, request_id)
    """
    tracker = get_performance_tracker()
    with tracker.track_operation(operation, context, **kwargs):
        yield


def setup_performance_logging(
    logger: Optional[logging.Logger] = None,
    config: Optional[PerformanceConfig] = None,
) -> PerformanceTracker:
    """Setup performance logging.

    Args:
        logger: Logger instance to use
        config: Performance configuration

    Returns:
        Configured performance tracker
    """
    global _global_tracker
    _global_tracker = PerformanceTracker(logger, config)
    return _global_tracker
