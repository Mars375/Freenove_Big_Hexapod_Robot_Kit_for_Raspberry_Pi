"""
Tachikoma - Launch API Server
"""
import uvicorn
from tachikoma.core.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("tachikoma.api.starting")
    uvicorn.run(
        "tachikoma.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
