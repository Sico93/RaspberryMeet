#!/usr/bin/env python3
"""
GPIO hardware test script.

Tests GPIO buttons and LEDs without browser automation.

Usage:
    python scripts/test_gpio.py

Hardware Requirements:
    - GPIO 17: Join/Leave button (with pull-up resistor)
    - GPIO 23: Green status LED (with resistor)
    - GPIO 24: Red status LED (with resistor)

Wiring:
    Button: GPIO 17 -> Button -> GND
    Green LED: GPIO 23 -> LED (with 220Ω resistor) -> GND
    Red LED: GPIO 24 -> LED (with 220Ω resistor) -> GND
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestrator.gpio_handler import GPIOHandler, LEDState
from src.utils.config import load_config
from src.utils.logger import setup_logger


logger = setup_logger("test_gpio", level="DEBUG")


async def test_leds(gpio: GPIOHandler):
    """Test all LED states."""
    logger.info("\n=== Testing LED States ===")

    states = [
        (LEDState.OFF, "Off (both LEDs off)"),
        (LEDState.GREEN, "Green (ready)"),
        (LEDState.RED, "Red (in meeting)"),
        (LEDState.YELLOW, "Yellow (both on - joining/leaving)"),
        (LEDState.BLINK_GREEN, "Blinking Green (processing)"),
        (LEDState.BLINK_RED, "Blinking Red (error)"),
    ]

    for state, description in states:
        logger.info(f"\nSetting LED: {description}")
        gpio.set_led_state(state)
        await asyncio.sleep(3)

    # Return to green (ready)
    logger.info("\nReturning to GREEN (ready)")
    gpio.set_led_state(LEDState.GREEN)


async def test_button(gpio: GPIOHandler):
    """Test button press detection."""
    logger.info("\n=== Testing Button ===")
    logger.info("Press the button on GPIO 17...")
    logger.info("(Each press will toggle LED between Green and Red)")
    logger.info("Press Ctrl+C to exit")

    # Track button state
    button_state = {"pressed_count": 0}

    async def button_callback():
        button_state["pressed_count"] += 1
        count = button_state["pressed_count"]

        logger.info(f"\n🔘 Button pressed! (Count: {count})")

        # Toggle LED color
        if count % 2 == 1:
            logger.info("   → Setting LED to RED")
            gpio.set_led_state(LEDState.RED)
        else:
            logger.info("   → Setting LED to GREEN")
            gpio.set_led_state(LEDState.GREEN)

    # Set button callback
    gpio.set_join_leave_callback(button_callback)

    # Wait for button presses
    try:
        while True:
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("\nTest stopped by user")


async def main():
    """Main test function."""
    logger.info("=" * 60)
    logger.info("🔧 GPIO Hardware Test")
    logger.info("=" * 60)

    # Load configuration
    config = load_config()

    logger.info(f"\nGPIO Configuration:")
    logger.info(f"  Enabled: {config.gpio.enabled}")
    logger.info(f"  Join/Leave Button Pin: GPIO {config.gpio.join_button_pin}")
    logger.info(f"  Green LED Pin: GPIO {config.gpio.status_led_green_pin}")
    logger.info(f"  Red LED Pin: GPIO {config.gpio.status_led_red_pin}")

    if not config.gpio.enabled:
        logger.warning("\n⚠️  GPIO is disabled in configuration (.env)")
        logger.warning("Set GPIO_ENABLED=true to enable GPIO")
        return 1

    # Create GPIO handler
    logger.info("\nInitializing GPIO handler...")
    gpio = GPIOHandler(config.gpio)

    if not gpio.enabled:
        logger.error("\n❌ GPIO initialization failed")
        logger.error("Make sure you are running on a Raspberry Pi with GPIO support")
        return 1

    try:
        # Test LEDs
        await test_leds(gpio)

        # Test button
        await test_button(gpio)

    except KeyboardInterrupt:
        logger.info("\n\nTest interrupted by user")

    finally:
        # Cleanup
        logger.info("\n=== Cleaning up GPIO ===")
        gpio.cleanup()

    logger.info("\n✅ GPIO test completed")
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)
