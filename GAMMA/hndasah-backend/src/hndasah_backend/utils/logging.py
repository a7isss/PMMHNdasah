"""
Logging configuration for WhatsApp PM System v3.0 (Gamma)
Structured logging with JSON output and proper formatting
"""

import sys
import structlog
from structlog import WriteLoggerFactory
from structlog.processors import JSONRenderer, TimeStamper
from structlog.dev import ConsoleRenderer
from ..config import settings


def setup_logging():
    """Configure structured logging for the application."""

    # Determine log format based on environment
    if settings.is_production():
        # JSON logging for production
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.stack_info,
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            JSONRenderer(),
        ]
    else:
        # Human-readable logging for development
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.stack_info,
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            ConsoleRenderer(colors=True),
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog, settings.LOG_LEVEL.upper(), structlog.INFO)
        ),
        context_class=dict,
        logger_factory=WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    import logging
    import logging.handlers

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add appropriate handler
    if settings.is_production():
        # JSON handler for production
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        )
        handler.setFormatter(formatter)
    else:
        # Colored console handler for development
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

    root_logger.addHandler(handler)

    # Configure specific loggers
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('alembic').setLevel(logging.INFO)

    # Suppress noisy third-party loggers
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('redis').setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.BoundLoggerBase:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


# Global logger instance
logger = get_logger(__name__)

