#!/usr/bin/env python3
"""
Quick demo script for BBB automation.

Before running:
1. Copy .env.example to .env
2. Configure BBB_DEFAULT_ROOM_URL in .env
3. Install Playwright: playwright install chromium

Usage:
    python demo_bbb_join.py
"""
import asyncio
from src.orchestrator.browser_controller import BrowserController
from src.utils.config import load_config
from src.utils.logger import setup_logger


async def demo():
    """Quick BBB join demo."""
    logger = setup_logger("demo", level="INFO")

    # Load config
    config = load_config()

    if not config.bbb.default_room_url:
        print("\n❌ ERROR: BBB_DEFAULT_ROOM_URL not configured!")
        print("Please edit .env file and set your BigBlueButton room URL\n")
        return

    print("\n🚀 RaspberryMeet BBB Demo")
    print(f"📍 Room: {config.bbb.default_room_url}")
    print(f"👤 Username: {config.bbb.default_username}")
    print("\n⏳ Starting browser and joining meeting...\n")

    # Create and use browser controller
    async with BrowserController(
        bbb_config=config.bbb,
        headless=False,
        kiosk_mode=False,
    ) as browser:
        # Join meeting
        success = await browser.join_meeting()

        if success:
            print("✅ Successfully joined meeting!")
            print("⏰ Staying in meeting for 60 seconds...")
            print("   (Press Ctrl+C to leave early)\n")

            try:
                await asyncio.sleep(60)
            except KeyboardInterrupt:
                print("\n⚠️  Leaving meeting early...")

            await browser.leave_meeting()
            print("👋 Left meeting\n")
        else:
            print("❌ Failed to join meeting")
            print("Check the logs above for details\n")


if __name__ == "__main__":
    try:
        asyncio.run(demo())
    except KeyboardInterrupt:
        print("\n\n👋 Demo cancelled\n")
