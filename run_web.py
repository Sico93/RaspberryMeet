#!/usr/bin/env python3
"""
Start the RaspberryMeet Web Admin Interface.

Usage:
    python run_web.py

The web interface will be available at:
    http://localhost:8080

Default credentials:
    Username: admin
    Password: change-this-password (configure in .env)
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn

from src.utils.config import load_config
from src.utils.logger import setup_logger


def main():
    """Start the web server."""
    logger = setup_logger("run_web", level="INFO")

    # Load configuration
    config = load_config()

    # Validate BBB configuration
    if not config.bbb.default_room_url:
        logger.warning("BBB_DEFAULT_ROOM_URL not configured in .env")
        logger.warning("Web interface will start but joining meetings may fail")

    # Start server
    logger.info("=" * 60)
    logger.info("🍓 Starting RaspberryMeet Web Admin Interface")
    logger.info("=" * 60)
    logger.info(f"URL: http://{config.web.host}:{config.web.port}")
    logger.info(f"Username: {config.web.username}")
    logger.info(f"Password: {'*' * len(config.web.password)}")
    logger.info("=" * 60)
    logger.info("\nPress CTRL+C to stop the server\n")

    try:
        uvicorn.run(
            "src.web.api:app",
            host=config.web.host,
            port=config.web.port,
            reload=False,  # Set to True for development
            log_level="info",
        )
    except KeyboardInterrupt:
        logger.info("\n\n👋 Shutting down web server...")


if __name__ == "__main__":
    main()
