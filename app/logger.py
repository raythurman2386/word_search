"""
Logging configuration for the Word Search Generator application.
Provides structured logging with JSON format for better compatibility with log aggregation tools.
"""

import logging
import os
import sys

from pythonjsonlogger import jsonlogger

from .config import settings


def setup_logger():
    """Configure and return the application logger."""
    logger = logging.getLogger("word_search")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    logger.handlers = []

    handlers = []

    console_handler = logging.StreamHandler(sys.stdout)
    handlers.append(console_handler)

    if settings.LOG_FILE:
        log_dir = os.path.dirname(settings.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(settings.LOG_FILE)
        handlers.append(file_handler)

    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        rename_fields={"levelname": "level", "asctime": "timestamp"},
    )

    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logger()
