"""
Configuration settings for the Word Search Generator application.
Uses pydantic-settings for type validation and loading from environment variables.
"""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "Word Search Generator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {"txt"}
    UPLOADS_DIR: str = "uploads"
    DOWNLOADS_DIR: str = "downloads"
    CLEANUP_INTERVAL_HOURS: int = 24
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None  # If None, logs to stdout only

    class Config:
        env_file = ".env"


settings = Settings()
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.DOWNLOADS_DIR, exist_ok=True)
