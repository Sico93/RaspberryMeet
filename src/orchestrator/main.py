"""
RaspberryMeet Main Orchestrator Service.

This is the main service that runs on the Raspberry Pi and manages:
- GPIO button/LED control
- BigBlueButton browser automation
- Meeting lifecycle management
- (Future: Calendar sync, auto-join, etc.)

Usage:
    python -m src.orchestrator.main

Or as systemd service:
    sudo systemctl start raspberrymeet
"""
import asyncio
import signal
import sys
from pathlib import Path

from src.orchestrator.meeting_manager import MeetingManager
from src.utils.config import load_config
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


# Global manager for signal handling
manager: MeetingManager = None
shutdown_event = asyncio.Event()


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {sig}, initiating shutdown...")
    shutdown_event.set()


async def main():
    """Main orchestrator entry point."""
    global manager

    logger.info("=" * 70)
    logger.info("🍓 RaspberryMeet Orchestrator Service Starting")
    logger.info("=" * 70)

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}", exc_info=True)
        return 1

    # Log configuration
    logger.info("\nConfiguration loaded:")
    logger.info(f"  Environment: {config.environment}")
    logger.info(f"  BBB Server: {config.bbb.server_url}")
    logger.info(f"  Default Room: {config.bbb.default_room_url}")
    logger.info(f"  GPIO Enabled: {config.gpio.enabled}")
    logger.info(f"  CalDAV Enabled: {config.caldav.enabled}")
    logger.info(f"  Kiosk Mode: {config.kiosk_mode}")
    logger.info(f"  Auto-Join on Boot: {config.auto_join_on_boot}")

    # Validate required configuration
    if not config.bbb.default_room_url:
        logger.error("\n❌ ERROR: BBB_DEFAULT_ROOM_URL not configured!")
        logger.error("Please configure your BigBlueButton room URL in .env")
        return 1

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create meeting manager
    logger.info("\n" + "=" * 70)
    logger.info("Initializing meeting manager...")
    logger.info("=" * 70 + "\n")

    manager = MeetingManager(config)

    try:
        # Start meeting manager
        await manager.start()

        logger.info("\n" + "=" * 70)
        logger.info("✅ RaspberryMeet Orchestrator Service is READY")
        logger.info("=" * 70)

        if config.gpio.enabled:
            logger.info("\n🎮 GPIO Control:")
            logger.info(f"   Press button on GPIO {config.gpio.join_button_pin} to join/leave meeting")
        else:
            logger.info("\n⚠️  GPIO is disabled - button control not available")

        logger.info("\n💡 LED Status Indicators:")
        logger.info("   🟢 Green: Ready for meeting")
        logger.info("   🟡 Yellow: Joining/Leaving")
        logger.info("   🔴 Red: In meeting")
        logger.info("   🔴 Blinking Red: Error")

        logger.info("\n📝 Press Ctrl+C or send SIGTERM to shutdown\n")

        # Auto-join on boot if configured
        if config.auto_join_on_boot:
            logger.info("🚀 AUTO_JOIN_ON_BOOT enabled - joining default meeting...")
            await asyncio.sleep(2)  # Wait for browser to stabilize
            await manager.join_default_meeting()

        # Status monitoring loop
        async def status_monitor():
            """Periodically log status."""
            while not shutdown_event.is_set():
                await asyncio.sleep(60)  # Every minute

                status = manager.get_status()
                logger.info(
                    f"📊 Status: {status['state'].upper()} | "
                    f"Room: {status['current_room'][:50] if status['current_room'] else 'None'} | "
                    f"Duration: {status['meeting_duration'] or 0}s"
                )

        # Start status monitor
        monitor_task = asyncio.create_task(status_monitor())

        # Wait for shutdown signal
        await shutdown_event.wait()

        # Cancel status monitor
        monitor_task.cancel()

        logger.info("\n" + "=" * 70)
        logger.info("Shutting down gracefully...")
        logger.info("=" * 70 + "\n")

        # Stop meeting manager
        await manager.stop()

        logger.info("✅ Shutdown complete")
        return 0

    except Exception as e:
        logger.error(f"Fatal error in orchestrator: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\nShutdown by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
