"""
GPIO hardware interface for buttons and LEDs.

Controls physical buttons and LED status indicators on Raspberry Pi.
"""
import asyncio
from enum import Enum
from typing import Callable, Optional

try:
    from gpiozero import Button, LED
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError) as e:
    # GPIO not available (not on Raspberry Pi or missing dependencies)
    GPIO_AVAILABLE = False
    print(f"GPIO not available: {e}")

from src.utils.config import GPIOConfig
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class LEDState(str, Enum):
    """LED state enumeration."""
    OFF = "off"
    GREEN = "green"
    RED = "red"
    YELLOW = "yellow"  # Both LEDs on
    BLINK_GREEN = "blink_green"
    BLINK_RED = "blink_red"


class MockButton:
    """Mock button for development without GPIO hardware."""

    def __init__(self, pin: int):
        self.pin = pin
        self._when_pressed = None
        logger.debug(f"Mock button created on pin {pin}")

    @property
    def when_pressed(self):
        return self._when_pressed

    @when_pressed.setter
    def when_pressed(self, callback):
        self._when_pressed = callback
        logger.debug(f"Button callback set for pin {self.pin}")

    def close(self):
        pass


class MockLED:
    """Mock LED for development without GPIO hardware."""

    def __init__(self, pin: int):
        self.pin = pin
        self._is_lit = False
        logger.debug(f"Mock LED created on pin {pin}")

    def on(self):
        self._is_lit = True
        logger.debug(f"LED {self.pin}: ON")

    def off(self):
        self._is_lit = False
        logger.debug(f"LED {self.pin}: OFF")

    def blink(self, on_time: float = 1, off_time: float = 1):
        logger.debug(f"LED {self.pin}: BLINKING (on={on_time}s, off={off_time}s)")

    def close(self):
        pass


class GPIOHandler:
    """
    GPIO hardware handler for buttons and LEDs.

    Manages physical button inputs and LED status indicators.
    Automatically falls back to mock implementation when GPIO is unavailable.
    """

    def __init__(self, config: GPIOConfig):
        """
        Initialize GPIO handler.

        Args:
            config: GPIO configuration
        """
        self.config = config
        self.enabled = config.enabled and GPIO_AVAILABLE

        # Button callbacks
        self._join_leave_callback: Optional[Callable] = None

        # Hardware components
        self.join_leave_button: Optional[Button] = None
        self.led_green: Optional[LED] = None
        self.led_red: Optional[LED] = None

        # State
        self.current_led_state = LEDState.OFF

        if not GPIO_AVAILABLE:
            logger.warning("GPIO hardware not available - using mock implementation")
            logger.warning("Button presses and LED changes will be logged only")

        if self.enabled:
            self._setup_hardware()
        else:
            logger.info("GPIO disabled in configuration")

    def _setup_hardware(self):
        """Setup GPIO hardware (buttons and LEDs)."""
        try:
            # Setup join/leave button
            if GPIO_AVAILABLE:
                self.join_leave_button = Button(
                    self.config.join_button_pin,
                    bounce_time=0.5,  # Debounce 500ms
                )
            else:
                self.join_leave_button = MockButton(self.config.join_button_pin)

            logger.info(f"Join/Leave button configured on GPIO {self.config.join_button_pin}")

            # Setup status LEDs
            if GPIO_AVAILABLE:
                self.led_green = LED(self.config.status_led_green_pin)
                self.led_red = LED(self.config.status_led_red_pin)
            else:
                self.led_green = MockLED(self.config.status_led_green_pin)
                self.led_red = MockLED(self.config.status_led_red_pin)

            logger.info(f"Status LEDs configured: Green={self.config.status_led_green_pin}, Red={self.config.status_led_red_pin}")

            # Set initial state (green = ready)
            self.set_led_state(LEDState.GREEN)

        except Exception as e:
            logger.error(f"Failed to setup GPIO hardware: {e}", exc_info=True)
            self.enabled = False

    def set_join_leave_callback(self, callback: Callable):
        """
        Set callback for join/leave button press.

        Args:
            callback: Async function to call when button is pressed
        """
        self._join_leave_callback = callback

        if self.join_leave_button:
            # Wrap async callback for gpiozero
            def sync_wrapper():
                if callback:
                    logger.debug("Join/Leave button pressed")
                    # Create task for async callback
                    asyncio.create_task(callback())

            self.join_leave_button.when_pressed = sync_wrapper
            logger.info("Join/Leave button callback registered")

    def set_led_state(self, state: LEDState):
        """
        Set LED status indicator state.

        Args:
            state: LED state to set
        """
        if not self.enabled or not self.led_green or not self.led_red:
            logger.debug(f"LED state change (mock): {state}")
            self.current_led_state = state
            return

        try:
            # Stop any blinking first
            self.led_green.off()
            self.led_red.off()

            if state == LEDState.OFF:
                # Both off
                pass

            elif state == LEDState.GREEN:
                # Green on, red off (system ready)
                self.led_green.on()

            elif state == LEDState.RED:
                # Red on, green off (in meeting)
                self.led_red.on()

            elif state == LEDState.YELLOW:
                # Both on (joining/leaving)
                self.led_green.on()
                self.led_red.on()

            elif state == LEDState.BLINK_GREEN:
                # Green blinking (waiting/processing)
                self.led_green.blink(on_time=0.5, off_time=0.5)

            elif state == LEDState.BLINK_RED:
                # Red blinking (error)
                self.led_red.blink(on_time=0.5, off_time=0.5)

            self.current_led_state = state
            logger.debug(f"LED state set to: {state}")

        except Exception as e:
            logger.error(f"Failed to set LED state: {e}")

    def cleanup(self):
        """Clean up GPIO resources."""
        logger.info("Cleaning up GPIO resources")

        try:
            if self.led_green:
                self.led_green.close()
            if self.led_red:
                self.led_red.close()
            if self.join_leave_button:
                self.join_leave_button.close()

            logger.info("GPIO cleanup complete")

        except Exception as e:
            logger.error(f"Error during GPIO cleanup: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
