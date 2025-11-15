"""
Browser automation controller for BigBlueButton using Playwright
"""
import asyncio
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
)

from src.utils.logger import setup_logger
from src.utils.config import BigBlueButtonConfig


logger = setup_logger(__name__)


class BrowserController:
    """
    Controls Chromium browser for automated BigBlueButton meeting joins.

    Supports both headless mode (for testing) and kiosk mode (for production).
    """

    def __init__(
        self,
        bbb_config: BigBlueButtonConfig,
        headless: bool = False,
        kiosk_mode: bool = True,
    ):
        """
        Initialize browser controller.

        Args:
            bbb_config: BigBlueButton configuration
            headless: Run browser in headless mode (no GUI)
            kiosk_mode: Run browser in fullscreen kiosk mode
        """
        self.bbb_config = bbb_config
        self.headless = headless
        self.kiosk_mode = kiosk_mode

        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        self._is_running = False

    async def start(self) -> None:
        """Start the browser and create a new page."""
        if self._is_running:
            logger.warning("Browser is already running")
            return

        logger.info("Starting Playwright browser...")

        try:
            self.playwright = await async_playwright().start()

            # Browser launch arguments
            launch_args = [
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-infobars",
                "--disable-session-crashed-bubble",
                "--disable-dev-shm-usage",
            ]

            # Add kiosk mode arguments if enabled
            if self.kiosk_mode and not self.headless:
                launch_args.extend([
                    "--kiosk",
                    "--start-fullscreen",
                ])

            # Launch browser
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=launch_args,
            )

            # Create browser context with permissions
            self.context = await self.browser.new_context(
                permissions=["microphone", "camera"],
                viewport={"width": 1920, "height": 1080} if not self.kiosk_mode else None,
            )

            # Create new page
            self.page = await self.context.new_page()

            self._is_running = True
            logger.info("Browser started successfully")

        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            await self.cleanup()
            raise

    async def join_meeting(
        self,
        room_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30000,
    ) -> bool:
        """
        Join a BigBlueButton meeting.

        Args:
            room_url: BBB room URL (uses default if not provided)
            username: Display name (uses default if not provided)
            password: Room password (uses default if not provided)
            timeout: Maximum time to wait for each step in milliseconds

        Returns:
            True if successfully joined, False otherwise
        """
        if not self._is_running or not self.page:
            logger.error("Browser is not running. Call start() first.")
            return False

        # Use defaults from config if not provided
        room_url = room_url or self.bbb_config.default_room_url
        username = username or self.bbb_config.default_username
        password = password or self.bbb_config.default_room_password

        if not room_url:
            logger.error("No room URL provided")
            return False

        logger.info(f"Joining BBB meeting as '{username}': {room_url}")

        try:
            # Navigate to room URL
            logger.debug(f"Navigating to {room_url}")
            await self.page.goto(room_url, wait_until="networkidle", timeout=timeout)
            await asyncio.sleep(2)  # Wait for page to stabilize

            # Handle room password if required
            if password:
                if await self._enter_room_password(password, timeout):
                    logger.debug("Room password entered successfully")

            # Enter username
            if not await self._enter_username(username, timeout):
                logger.error("Failed to enter username")
                return False

            # Click join button
            if not await self._click_join_button(timeout):
                logger.error("Failed to click join button")
                return False

            # Wait for meeting to load
            await asyncio.sleep(3)

            # Handle audio setup
            if not await self._setup_audio(timeout):
                logger.warning("Failed to setup audio, but continuing...")

            # Close any welcome/tutorial modals
            await self._close_modals(timeout)

            logger.info("Successfully joined BBB meeting")
            return True

        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout while joining meeting: {e}")
            return False
        except Exception as e:
            logger.error(f"Error joining meeting: {e}")
            return False

    async def _enter_room_password(self, password: str, timeout: int) -> bool:
        """Enter room password if prompted."""
        try:
            # Look for password input field
            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "input[placeholder*='password' i]",
                "input[placeholder*='passwort' i]",
            ]

            for selector in password_selectors:
                try:
                    password_input = await self.page.wait_for_selector(
                        selector, timeout=5000
                    )
                    if password_input:
                        logger.debug(f"Found password input: {selector}")
                        await password_input.fill(password)

                        # Try to find and click submit button
                        submit_selectors = [
                            "button[type='submit']",
                            "button:has-text('Submit')",
                            "button:has-text('Enter')",
                            "button:has-text('Join')",
                        ]

                        for submit_selector in submit_selectors:
                            try:
                                submit_btn = await self.page.wait_for_selector(
                                    submit_selector, timeout=2000
                                )
                                if submit_btn:
                                    await submit_btn.click()
                                    await asyncio.sleep(2)
                                    return True
                            except PlaywrightTimeoutError:
                                continue

                        # If no submit button found, press Enter
                        await password_input.press("Enter")
                        await asyncio.sleep(2)
                        return True

                except PlaywrightTimeoutError:
                    continue

            # No password field found
            return False

        except Exception as e:
            logger.debug(f"No password prompt found or error: {e}")
            return False

    async def _enter_username(self, username: str, timeout: int) -> bool:
        """Enter username in BBB join screen."""
        try:
            # Common username field selectors
            username_selectors = [
                "input[aria-label*='name' i]",
                "input[placeholder*='name' i]",
                "input[type='text']",
                "input[id*='name' i]",
                "#input-name",
            ]

            for selector in username_selectors:
                try:
                    username_input = await self.page.wait_for_selector(
                        selector, timeout=5000
                    )
                    if username_input:
                        logger.debug(f"Found username input: {selector}")
                        await username_input.fill(username)
                        await asyncio.sleep(1)
                        return True
                except PlaywrightTimeoutError:
                    continue

            logger.error("Could not find username input field")
            return False

        except Exception as e:
            logger.error(f"Error entering username: {e}")
            return False

    async def _click_join_button(self, timeout: int) -> bool:
        """Click the join meeting button."""
        try:
            # Common join button selectors
            join_selectors = [
                "button:has-text('Join')",
                "button:has-text('Beitreten')",
                "button[aria-label*='join' i]",
                "button[type='submit']",
                ".join-button",
            ]

            for selector in join_selectors:
                try:
                    join_button = await self.page.wait_for_selector(
                        selector, timeout=5000
                    )
                    if join_button:
                        logger.debug(f"Found join button: {selector}")
                        await join_button.click()
                        await asyncio.sleep(3)
                        return True
                except PlaywrightTimeoutError:
                    continue

            logger.error("Could not find join button")
            return False

        except Exception as e:
            logger.error(f"Error clicking join button: {e}")
            return False

    async def _setup_audio(self, timeout: int) -> bool:
        """Setup audio (microphone) for the meeting."""
        try:
            # Look for "Join Audio" or "Microphone" button
            audio_selectors = [
                "button:has-text('Microphone')",
                "button:has-text('Mikrofon')",
                "button:has-text('Join audio')",
                "button:has-text('Audio beitreten')",
                "button[aria-label*='microphone' i]",
                "button[aria-label*='audio' i]",
            ]

            for selector in audio_selectors:
                try:
                    audio_button = await self.page.wait_for_selector(
                        selector, timeout=10000
                    )
                    if audio_button:
                        logger.debug(f"Found audio button: {selector}")
                        await audio_button.click()
                        await asyncio.sleep(2)

                        # Look for echo test modal and skip it
                        await self._skip_echo_test(timeout)

                        return True
                except PlaywrightTimeoutError:
                    continue

            logger.warning("Could not find audio setup button")
            return False

        except Exception as e:
            logger.error(f"Error setting up audio: {e}")
            return False

    async def _skip_echo_test(self, timeout: int) -> bool:
        """Skip the audio echo test if prompted."""
        try:
            # Look for echo test confirmation button
            confirm_selectors = [
                "button:has-text('Yes')",
                "button:has-text('Ja')",
                "button:has-text('Confirm')",
                "button:has-text('Bestätigen')",
            ]

            for selector in confirm_selectors:
                try:
                    confirm_button = await self.page.wait_for_selector(
                        selector, timeout=5000
                    )
                    if confirm_button:
                        logger.debug("Confirming echo test")
                        await confirm_button.click()
                        await asyncio.sleep(1)
                        return True
                except PlaywrightTimeoutError:
                    continue

            return False

        except Exception as e:
            logger.debug(f"No echo test prompt or error: {e}")
            return False

    async def _close_modals(self, timeout: int) -> None:
        """Close any welcome or tutorial modals."""
        try:
            # Look for close/dismiss buttons
            close_selectors = [
                "button[aria-label*='close' i]",
                "button[aria-label*='dismiss' i]",
                "button:has-text('OK')",
                "button:has-text('Got it')",
                "button:has-text('Verstanden')",
                ".modal-close",
            ]

            for selector in close_selectors:
                try:
                    close_button = await self.page.wait_for_selector(
                        selector, timeout=3000
                    )
                    if close_button:
                        logger.debug(f"Closing modal: {selector}")
                        await close_button.click()
                        await asyncio.sleep(1)
                except PlaywrightTimeoutError:
                    continue

        except Exception as e:
            logger.debug(f"No modals to close or error: {e}")

    async def leave_meeting(self) -> bool:
        """Leave the current meeting."""
        if not self._is_running or not self.page:
            logger.warning("Browser is not running")
            return False

        try:
            logger.info("Leaving BBB meeting")

            # Look for options/settings menu
            options_selectors = [
                "button[aria-label*='options' i]",
                "button[aria-label*='settings' i]",
                "button[data-test='optionsButton']",
            ]

            for selector in options_selectors:
                try:
                    options_button = await self.page.wait_for_selector(
                        selector, timeout=5000
                    )
                    if options_button:
                        await options_button.click()
                        await asyncio.sleep(1)
                        break
                except PlaywrightTimeoutError:
                    continue

            # Look for leave/logout button
            leave_selectors = [
                "button:has-text('Leave')",
                "button:has-text('Logout')",
                "button:has-text('Verlassen')",
                "button:has-text('Abmelden')",
                "li:has-text('Leave')",
                "li:has-text('Logout')",
            ]

            for selector in leave_selectors:
                try:
                    leave_button = await self.page.wait_for_selector(
                        selector, timeout=5000
                    )
                    if leave_button:
                        await leave_button.click()
                        await asyncio.sleep(2)
                        logger.info("Left meeting successfully")
                        return True
                except PlaywrightTimeoutError:
                    continue

            logger.warning("Could not find leave button, closing page instead")
            await self.page.close()
            self.page = await self.context.new_page()
            return True

        except Exception as e:
            logger.error(f"Error leaving meeting: {e}")
            return False

    async def is_in_meeting(self) -> bool:
        """Check if currently in a meeting."""
        if not self._is_running or not self.page:
            return False

        try:
            # Check for BBB video grid or meeting indicators
            meeting_indicators = [
                "[data-test='videoPreviewElement']",
                "[data-test='webcamConnecting']",
                "[class*='videoGrid']",
                "[class*='presentation']",
            ]

            for selector in meeting_indicators:
                try:
                    element = await self.page.wait_for_selector(
                        selector, timeout=2000
                    )
                    if element:
                        return True
                except PlaywrightTimeoutError:
                    continue

            return False

        except Exception:
            return False

    async def cleanup(self) -> None:
        """Clean up browser resources."""
        logger.info("Cleaning up browser resources")

        try:
            if self.page:
                await self.page.close()
                self.page = None

            if self.context:
                await self.context.close()
                self.context = None

            if self.browser:
                await self.browser.close()
                self.browser = None

            if self.playwright:
                await self.playwright.stop()
                self.playwright = None

            self._is_running = False
            logger.info("Browser cleanup complete")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
