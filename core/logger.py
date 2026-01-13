"""
Structured logging setup using structlog.
Provides JSON logging for production and pretty console logging for development.
"""
import logging
import sys
from pathlib import Path
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from core.config import settings


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application context to all log entries."""
    event_dict["app"] = settings.app_name
    event_dict["version"] = settings.app_version
    event_dict["environment"] = settings.environment
    event_dict["robot"] = settings.robot_name
    return event_dict


def setup_logging() -> None:
    """
    Configure structured logging for the application.
    
    - Development: Pretty console output with colors
    - Production: JSON output for log aggregation
    """
    # Ensure log directory exists
    settings.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )
    
    # Common processors for all environments
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_app_context,
    ]
    
    # Add environment-specific processors
    if settings.is_development:
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True)
        ])
    else:
        processors.extend([
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ])
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured structlog logger
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("robot.started", speed=5, position=(0, 0))
    """
    return structlog.get_logger(name)


# Initialize logging on module import
setup_logging()

# Default logger
logger = get_logger(__name__)
