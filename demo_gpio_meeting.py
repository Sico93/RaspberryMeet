#!/usr/bin/env python3
"""
GPIO Meeting Control Demo.

Demonstrates GPIO button control for joining/leaving BBB meetings.

Usage:
    python demo_gpio_meeting.py

Features:
    - Press button to join default BBB room
    - Press again to leave meeting
    - LED indicators show status:
      - Green: Ready for meeting
      - Yellow: Joining/Leaving
      - Red: In meeting
      - Blinking Red: Error

Hardware:
    - GPIO 17: Join/Leave button
    - GPIO 23: Green status LED
    - GPIO 24: Red status LED
"""
import asyncio
import signal
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.orchestrator.meeting_manager import MeetingManager
from src.utils.config import load_config
from src.utils.logger import setup_logger


logger = setup_logger("demo_gpio", level="INFO")


# Global manager for signal handling
manager = None


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    logger.info("\n\n⚠️  Shutting down...")
    if manager:
        asyncio.create_task(manager.stop())
    sys.exit(0)


async def status_monitor(manager: MeetingManager):
    """Monitor and display meeting status periodically."""
    while True:
        await asyncio.sleep(5)

        status = manager.get_status()
        logger.info(
            f"📊 Status: {status['state'].upper()} | "
            f"Room: {status['current_room'] or 'None'} | "
            f"Duration: {status['meeting_duration'] or 0}s | "
            f"LED: {status['led_state']}"
        )


async def main():
    """Main demo function."""
    global manager

    logger.info("=" * 70)
    logger.info("🍓 RaspberryMeet GPIO Meeting Control Demo")
    logger.info("=" * 70)

    # Load configuration
    config = load_config()

    # Validate configuration
    if not config.bbb.default_room_url:
        logger.error("\n❌ ERROR: BBB_DEFAULT_ROOM_URL not configured!")
        logger.error("Please edit .env file and set your BigBlueButton room URL\n")
        return 1

    logger.info(f"\nConfiguration:")
    logger.info(f"  BBB Room: {config.bbb.default_room_url}")
    logger.info(f"  Username: {config.bbb.default_username}")
    logger.info(f"  GPIO Enabled: {config.gpio.enabled}")
    logger.info(f"  Join/Leave Button: GPIO {config.gpio.join_button_pin}")
    logger.info(f"  Green LED: GPIO {config.gpio.status_led_green_pin}")
    logger.info(f"  Red LED: GPIO {config.gpio.status_led_red_pin}")
    logger.info(f"  Kiosk Mode: {config.kiosk_mode}")

    logger.info("\n" + "=" * 70)
    logger.info("🎮 Controls:")
    logger.info("  - Press button on GPIO 17 to JOIN default meeting")
    logger.info("  - Press button again to LEAVE meeting")
    logger.info("  - Press Ctrl+C to exit")
    logger.info("=" * 70)
    logger.info("\n💡 LED Status:")
    logger.info("  🟢 Green: Ready for meeting")
    logger.info("  🟡 Yellow (both): Joining or leaving")
    logger.info("  🔴 Red: In meeting")
    logger.info("  🔴 Blinking Red: Error occurred")
    logger.info("=" * 70)

    if not config.gpio.enabled:
        logger.warning("\n⚠️  GPIO is DISABLED in configuration")
        logger.warning("The demo will work, but button presses will be simulated in logs only")
        logger.warning("Set GPIO_ENABLED=true in .env to enable actual hardware\n")

    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start meeting manager
    logger.info("\n🚀 Starting meeting manager...\n")

    manager = MeetingManager(config)

    try:
        async with manager:
            logger.info("✅ Meeting manager ready!")
            logger.info("   System is IDLE - press button to join meeting\n")

            # Start status monitor
            monitor_task = asyncio.create_task(status_monitor(manager))

            # Keep running until interrupted
            try:
                await asyncio.Future()  # Run forever
            except asyncio.CancelledError:
                monitor_task.cancel()

    except KeyboardInterrupt:
        logger.info("\n\n👋 Demo stopped by user")

    except Exception as e:
        logger.error(f"\n❌ Demo failed: {e}", exc_info=True)
        return 1

    logger.info("\n✅ Demo completed\n")
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n\n👋 Cancelled\n")
        sys.exit(0)
