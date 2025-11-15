"""
Meeting lifecycle manager.

Orchestrates browser automation, GPIO control, and meeting state.
"""
import asyncio
from datetime import datetime
from enum import Enum
from typing import Optional

from src.orchestrator.browser_controller import BrowserController
from src.orchestrator.gpio_handler import GPIOHandler, LEDState
from src.utils.config import AppConfig
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class MeetingState(str, Enum):
    """Meeting state enumeration."""
    IDLE = "idle"
    JOINING = "joining"
    ACTIVE = "active"
    LEAVING = "leaving"
    ERROR = "error"


class MeetingManager:
    """
    Manages meeting lifecycle and hardware integration.

    Coordinates browser automation, GPIO buttons/LEDs, and meeting state.
    """

    def __init__(self, config: AppConfig):
        """
        Initialize meeting manager.

        Args:
            config: Application configuration
        """
        self.config = config

        # Components
        self.browser: Optional[BrowserController] = None
        self.gpio: Optional[GPIOHandler] = None

        # State
        self.state = MeetingState.IDLE
        self.current_room_url: Optional[str] = None
        self.meeting_start_time: Optional[datetime] = None

        # Lock for state transitions
        self._state_lock = asyncio.Lock()

        logger.info("Meeting manager initialized")

    async def start(self):
        """Start the meeting manager and initialize components."""
        logger.info("Starting meeting manager...")

        # Initialize browser controller
        self.browser = BrowserController(
            bbb_config=self.config.bbb,
            headless=False,  # Show browser for GPIO mode
            kiosk_mode=self.config.kiosk_mode,
        )
        await self.browser.start()
        logger.info("Browser controller started")

        # Initialize GPIO handler
        if self.config.gpio.enabled:
            self.gpio = GPIOHandler(self.config.gpio)
            self.gpio.set_join_leave_callback(self._handle_join_leave_button)
            logger.info("GPIO handler started")
        else:
            logger.info("GPIO disabled - button control not available")

        # Set initial LED state
        if self.gpio:
            self.gpio.set_led_state(LEDState.GREEN)

        logger.info("Meeting manager started successfully")

    async def stop(self):
        """Stop the meeting manager and cleanup resources."""
        logger.info("Stopping meeting manager...")

        # Leave meeting if active
        if self.state == MeetingState.ACTIVE:
            await self.leave_meeting()

        # Cleanup components
        if self.browser:
            await self.browser.cleanup()

        if self.gpio:
            self.gpio.cleanup()

        logger.info("Meeting manager stopped")

    async def _handle_join_leave_button(self):
        """
        Handle join/leave button press (toggle behavior).

        - If IDLE: Join default meeting
        - If ACTIVE: Leave meeting
        - Otherwise: Ignore (already transitioning)
        """
        async with self._state_lock:
            logger.info(f"Button pressed. Current state: {self.state}")

            if self.state == MeetingState.IDLE:
                # Join default meeting
                logger.info("Button action: Joining default meeting")
                await self.join_default_meeting()

            elif self.state == MeetingState.ACTIVE:
                # Leave current meeting
                logger.info("Button action: Leaving meeting")
                await self.leave_meeting()

            else:
                # Busy (joining/leaving) - ignore button press
                logger.warning(f"Button press ignored - system busy (state: {self.state})")

    async def join_default_meeting(self) -> bool:
        """
        Join the default BigBlueButton meeting.

        Returns:
            True if successfully joined, False otherwise
        """
        return await self.join_meeting(
            room_url=self.config.bbb.default_room_url,
            username=self.config.bbb.default_username,
            password=self.config.bbb.default_room_password,
        )

    async def join_meeting(
        self,
        room_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> bool:
        """
        Join a BigBlueButton meeting.

        Args:
            room_url: BBB room URL (uses default if not provided)
            username: Display name (uses default if not provided)
            password: Room password (uses default if not provided)

        Returns:
            True if successfully joined, False otherwise
        """
        if self.state != MeetingState.IDLE:
            logger.error(f"Cannot join - not idle (current state: {self.state})")
            return False

        # Update state
        self.state = MeetingState.JOINING
        self.current_room_url = room_url or self.config.bbb.default_room_url

        # Update LED to yellow (joining)
        if self.gpio:
            self.gpio.set_led_state(LEDState.YELLOW)

        logger.info(f"Joining meeting: {self.current_room_url}")

        try:
            # Join meeting via browser automation
            success = await self.browser.join_meeting(
                room_url=room_url,
                username=username,
                password=password,
            )

            if success:
                # Successfully joined
                self.state = MeetingState.ACTIVE
                self.meeting_start_time = datetime.now()

                # Update LED to red (in meeting)
                if self.gpio:
                    self.gpio.set_led_state(LEDState.RED)

                logger.info("Successfully joined meeting")
                return True

            else:
                # Failed to join
                self.state = MeetingState.ERROR

                # Update LED to blinking red (error)
                if self.gpio:
                    self.gpio.set_led_state(LEDState.BLINK_RED)

                logger.error("Failed to join meeting")

                # Auto-reset to idle after 5 seconds
                asyncio.create_task(self._auto_reset_from_error())

                return False

        except Exception as e:
            logger.error(f"Exception while joining meeting: {e}", exc_info=True)

            self.state = MeetingState.ERROR
            if self.gpio:
                self.gpio.set_led_state(LEDState.BLINK_RED)

            asyncio.create_task(self._auto_reset_from_error())

            return False

    async def leave_meeting(self) -> bool:
        """
        Leave the current meeting.

        Returns:
            True if successfully left, False otherwise
        """
        if self.state != MeetingState.ACTIVE:
            logger.error(f"Cannot leave - not in meeting (current state: {self.state})")
            return False

        # Update state
        self.state = MeetingState.LEAVING

        # Update LED to yellow (leaving)
        if self.gpio:
            self.gpio.set_led_state(LEDState.YELLOW)

        logger.info("Leaving meeting")

        try:
            # Leave meeting via browser automation
            await self.browser.leave_meeting()

            # Successfully left
            self.state = MeetingState.IDLE
            self.current_room_url = None
            self.meeting_start_time = None

            # Update LED to green (ready)
            if self.gpio:
                self.gpio.set_led_state(LEDState.GREEN)

            logger.info("Successfully left meeting")
            return True

        except Exception as e:
            logger.error(f"Exception while leaving meeting: {e}", exc_info=True)

            self.state = MeetingState.ERROR
            if self.gpio:
                self.gpio.set_led_state(LEDState.BLINK_RED)

            asyncio.create_task(self._auto_reset_from_error())

            return False

    async def _auto_reset_from_error(self):
        """Automatically reset from error state to idle after delay."""
        await asyncio.sleep(5)

        if self.state == MeetingState.ERROR:
            logger.info("Auto-resetting from error state to idle")
            self.state = MeetingState.IDLE
            self.current_room_url = None
            self.meeting_start_time = None

            if self.gpio:
                self.gpio.set_led_state(LEDState.GREEN)

    def get_status(self) -> dict:
        """
        Get current meeting status.

        Returns:
            Status dictionary with state, room, duration, etc.
        """
        duration = None
        if self.meeting_start_time and self.state == MeetingState.ACTIVE:
            duration = int((datetime.now() - self.meeting_start_time).total_seconds())

        return {
            "state": self.state.value,
            "current_room": self.current_room_url,
            "meeting_duration": duration,
            "gpio_enabled": self.config.gpio.enabled,
            "led_state": self.gpio.current_led_state.value if self.gpio else None,
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
