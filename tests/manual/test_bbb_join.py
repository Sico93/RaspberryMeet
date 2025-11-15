#!/usr/bin/env python3
"""
Manual test script for BBB browser automation.

Usage:
    python tests/manual/test_bbb_join.py

This script will:
1. Load configuration from .env file
2. Launch Chromium browser
3. Attempt to join the default BBB room
4. Wait for 30 seconds in the meeting
5. Leave the meeting and cleanup
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.orchestrator.browser_controller import BrowserController
from src.utils.config import load_config
from src.utils.logger import setup_logger


logger = setup_logger("test_bbb_join", level="DEBUG")


async def main():
    """Main test function."""
    logger.info("=== BBB Browser Automation Test ===")

    # Load configuration
    logger.info("Loading configuration from .env...")
    config = load_config()

    # Validate configuration
    if not config.bbb.default_room_url:
        logger.error("BBB_DEFAULT_ROOM_URL not set in .env file")
        logger.error("Please configure your BigBlueButton room URL")
        return 1

    logger.info(f"BBB Server: {config.bbb.server_url}")
    logger.info(f"Default Room: {config.bbb.default_room_url}")
    logger.info(f"Username: {config.bbb.default_username}")
    logger.info(f"Password configured: {'Yes' if config.bbb.default_room_password else 'No'}")

    # Create browser controller
    # Use headless=False to see the browser in action
    # Set kiosk_mode=False for easier debugging (can see browser UI)
    browser = BrowserController(
        bbb_config=config.bbb,
        headless=False,  # Change to True for headless testing
        kiosk_mode=False,  # Change to True for fullscreen kiosk mode
    )

    try:
        # Start browser
        logger.info("\n--- Starting browser ---")
        await browser.start()

        # Join meeting
        logger.info("\n--- Joining BBB meeting ---")
        success = await browser.join_meeting()

        if not success:
            logger.error("Failed to join meeting")
            return 1

        logger.info("Successfully joined meeting!")

        # Check if in meeting
        in_meeting = await browser.is_in_meeting()
        logger.info(f"In meeting check: {in_meeting}")

        # Stay in meeting for 30 seconds
        logger.info("\n--- Staying in meeting for 30 seconds ---")
        logger.info("(You should see the BBB interface now)")
        await asyncio.sleep(30)

        # Leave meeting
        logger.info("\n--- Leaving meeting ---")
        await browser.leave_meeting()

        logger.info("\n=== Test completed successfully ===")
        return 0

    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        return 1

    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        return 1

    finally:
        # Cleanup
        logger.info("\n--- Cleaning up ---")
        await browser.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
