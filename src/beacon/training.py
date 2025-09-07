"""
Training event logging utilities for Beacon.
"""

import logging
from typing import Any, Dict, Optional

import structlog

from .config import TrainingLoggingConfig


class TrainingLogger:
    """Handles training event logging with structured data."""

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        config: Optional[TrainingLoggingConfig] = None,
    ):
        self.logger = logger or logging.getLogger("training")
        self.config = config or TrainingLoggingConfig()

    def log_training_event(
        self,
        session_id: str,
        event_type: str,
        **kwargs,
    ) -> None:
        """Log a training-related event.

        Args:
            session_id: Training session identifier
            event_type: Type of training event
            **kwargs: Additional event data
        """
        log_data = {
            "session_id": session_id,
            "event_type": event_type,
        }
        log_data.update(kwargs)

        self.logger.info(f"Training event: {event_type}", extra=log_data)

    def log_model_event(
        self,
        model_id: int,
        event_type: str,
        **kwargs,
    ) -> None:
        """Log a model-related event.

        Args:
            model_id: Model identifier
            event_type: Type of model event
            **kwargs: Additional event data
        """
        log_data = {
            "model_id": model_id,
            "event_type": event_type,
        }
        log_data.update(kwargs)

        self.logger.info(f"Model event: {event_type}", extra=log_data)

    def log_training_start(
        self,
        session_id: str,
        model_name: str,
        hyperparameters: Optional[Dict[str, Any]] = None,
        dataset_info: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        """Log training start event.

        Args:
            session_id: Training session identifier
            model_name: Name of the model being trained
            hyperparameters: Model hyperparameters
            dataset_info: Dataset information
            **kwargs: Additional context
        """
        event_data = {
            "model_name": model_name,
        }

        if self.config.log_hyperparameters and hyperparameters:
            event_data["hyperparameters"] = hyperparameters

        if dataset_info:
            event_data["dataset_info"] = dataset_info

        event_data.update(kwargs)

        self.log_training_event(session_id, "training_start", **event_data)

    def log_training_step(
        self,
        session_id: str,
        step: int,
        epoch: int,
        loss: float,
        metrics: Optional[Dict[str, float]] = None,
        **kwargs,
    ) -> None:
        """Log training step event.

        Args:
            session_id: Training session identifier
            step: Current training step
            epoch: Current epoch
            loss: Current loss value
            metrics: Additional metrics
            **kwargs: Additional context
        """
        event_data = {
            "step": step,
            "epoch": epoch,
            "loss": loss,
        }

        if self.config.log_metrics and metrics:
            event_data["metrics"] = metrics

        event_data.update(kwargs)

        self.log_training_event(session_id, "training_step", **event_data)

    def log_validation(
        self,
        session_id: str,
        epoch: int,
        validation_loss: float,
        validation_metrics: Optional[Dict[str, float]] = None,
        **kwargs,
    ) -> None:
        """Log validation event.

        Args:
            session_id: Training session identifier
            epoch: Current epoch
            validation_loss: Validation loss
            validation_metrics: Validation metrics
            **kwargs: Additional context
        """
        event_data = {
            "epoch": epoch,
            "validation_loss": validation_loss,
        }

        if self.config.log_validation and validation_metrics:
            event_data["validation_metrics"] = validation_metrics

        event_data.update(kwargs)

        self.log_training_event(session_id, "validation", **event_data)

    def log_checkpoint(
        self,
        session_id: str,
        checkpoint_path: str,
        epoch: int,
        metrics: Optional[Dict[str, float]] = None,
        **kwargs,
    ) -> None:
        """Log checkpoint save event.

        Args:
            session_id: Training session identifier
            checkpoint_path: Path to saved checkpoint
            epoch: Current epoch
            metrics: Metrics at checkpoint
            **kwargs: Additional context
        """
        event_data = {
            "checkpoint_path": checkpoint_path,
            "epoch": epoch,
        }

        if self.config.log_checkpoints and metrics:
            event_data["metrics"] = metrics

        event_data.update(kwargs)

        self.log_training_event(session_id, "checkpoint_saved", **event_data)

    def log_training_end(
        self,
        session_id: str,
        final_metrics: Optional[Dict[str, float]] = None,
        training_time: Optional[float] = None,
        **kwargs,
    ) -> None:
        """Log training end event.

        Args:
            session_id: Training session identifier
            final_metrics: Final training metrics
            training_time: Total training time in seconds
            **kwargs: Additional context
        """
        event_data = {}

        if self.config.log_metrics and final_metrics:
            event_data["final_metrics"] = final_metrics

        if training_time:
            event_data["training_time"] = training_time

        event_data.update(kwargs)

        self.log_training_event(session_id, "training_end", **event_data)

    def log_model_save(
        self,
        model_id: int,
        model_path: str,
        model_info: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        """Log model save event.

        Args:
            model_id: Model identifier
            model_path: Path where model was saved
            model_info: Model information
            **kwargs: Additional context
        """
        event_data = {
            "model_path": model_path,
        }

        if model_info:
            event_data["model_info"] = model_info

        event_data.update(kwargs)

        self.log_model_event(model_id, "model_saved", **event_data)

    def log_model_load(
        self,
        model_id: int,
        model_path: str,
        **kwargs,
    ) -> None:
        """Log model load event.

        Args:
            model_id: Model identifier
            model_path: Path from where model was loaded
            **kwargs: Additional context
        """
        event_data = {
            "model_path": model_path,
        }
        event_data.update(kwargs)

        self.log_model_event(model_id, "model_loaded", **event_data)


def log_training_event(
    logger: structlog.BoundLogger,
    session_id: str,
    event_type: str,
    **kwargs: Any,
) -> None:
    """Log training-related events.

    This function maintains compatibility with the original implementation.

    Args:
        logger: Structured logger instance
        session_id: Training session identifier
        event_type: Type of training event
        **kwargs: Additional event data
    """
    logger.info(
        "Training event",
        session_id=session_id,
        event_type=event_type,
        **kwargs,
    )


def log_model_event(
    logger: structlog.BoundLogger,
    model_id: int,
    event_type: str,
    **kwargs: Any,
) -> None:
    """Log model-related events.

    This function maintains compatibility with the original implementation.

    Args:
        logger: Structured logger instance
        model_id: Model identifier
        event_type: Type of model event
        **kwargs: Additional event data
    """
    logger.info(
        "Model event",
        model_id=model_id,
        event_type=event_type,
        **kwargs,
    )


def setup_training_logging(
    logger: Optional[logging.Logger] = None,
    config: Optional[TrainingLoggingConfig] = None,
) -> TrainingLogger:
    """Setup training logging.

    Args:
        logger: Logger instance to use
        config: Training logging configuration

    Returns:
        Configured training logger
    """
    return TrainingLogger(logger, config)
