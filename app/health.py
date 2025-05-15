"""
Health check endpoint for monitoring the application status.
"""
from fastapi import APIRouter, HTTPException
import os
from .config import settings
from .logger import logger

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check if uploads directory is accessible
        if not os.path.exists(settings.UPLOADS_DIR) or not os.access(settings.UPLOADS_DIR, os.W_OK):
            logger.error(f"Uploads directory not accessible: {settings.UPLOADS_DIR}")
            raise HTTPException(status_code=503, detail="Storage not accessible")
        
        # Check if downloads directory is accessible
        if not os.path.exists(settings.DOWNLOADS_DIR) or not os.access(settings.DOWNLOADS_DIR, os.W_OK):
            logger.error(f"Downloads directory not accessible: {settings.DOWNLOADS_DIR}")
            raise HTTPException(status_code=503, detail="Storage not accessible")
            
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "storage": {
                "uploads": os.path.exists(settings.UPLOADS_DIR),
                "downloads": os.path.exists(settings.DOWNLOADS_DIR)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
