"""
Calendar-based meeting scheduler for RaspberryMeet.

Automatically joins BigBlueButton meetings based on CalDAV calendar events.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Callable, List, Dict
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.orchestrator.calendar_sync import CalDAVClient, MeetingEvent, create_caldav_client
from src.utils.config import CalDAVConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CalendarScheduler:
    """
    Scheduler for automatic meeting joins based on calendar events.

    Periodically syncs with CalDAV server, detects upcoming meetings,
    and triggers automatic joins at the appropriate time.
    """

    def __init__(
        self,
        caldav_config: CalDAVConfig,
        on_meeting_start: Optional[Callable[[MeetingEvent], asyncio.Future]] = None,
        use_mock: bool = False
    ):
        """
        Initialize calendar scheduler.

        Args:
            caldav_config: CalDAV configuration
            on_meeting_start: Async callback when meeting should be joined
            use_mock: Use mock CalDAV client for testing
        """
        self.config = caldav_config
        self.on_meeting_start = on_meeting_start
        self.use_mock = use_mock

        # CalDAV client
        self.caldav_client: Optional[CalDAVClient] = None

        # Scheduler
        self.scheduler: Optional[AsyncIOScheduler] = None

        # Tracking
        self.upcoming_meetings: List[MeetingEvent] = []
        self.joined_meetings: Dict[str, MeetingEvent] = {}  # uid -> event
        self.last_sync: Optional[datetime] = None

        # State
        self.is_running = False

    async def start(self):
        """Start the calendar scheduler."""
        if self.is_running:
            logger.warning("Calendar scheduler already running")
            return

        if not self.config.enabled:
            logger.info("CalDAV sync is disabled in configuration")
            return

        if not self.config.url or not self.config.username or not self.config.password:
            logger.error("CalDAV credentials not configured")
            return

        logger.info("Starting calendar scheduler...")

        # Create and connect CalDAV client
        self.caldav_client = create_caldav_client(
            url=self.config.url,
            username=self.config.username,
            password=self.config.password,
            calendar_name=self.config.calendar_name,
            use_mock=self.use_mock
        )

        if not self.caldav_client.connect():
            logger.error("Failed to connect to CalDAV server")
            return

        # Create scheduler
        self.scheduler = AsyncIOScheduler()

        # Schedule periodic sync
        sync_interval = self.config.sync_interval_minutes
        self.scheduler.add_job(
            self._sync_calendar,
            trigger=IntervalTrigger(minutes=sync_interval),
            id="calendar_sync",
            name="Sync calendar events",
            replace_existing=True
        )
        logger.info(f"Scheduled calendar sync every {sync_interval} minutes")

        # Schedule meeting check
        check_interval = self.config.check_interval_seconds
        self.scheduler.add_job(
            self._check_upcoming_meetings,
            trigger=IntervalTrigger(seconds=check_interval),
            id="meeting_check",
            name="Check for upcoming meetings",
            replace_existing=True
        )
        logger.info(f"Scheduled meeting check every {check_interval} seconds")

        # Start scheduler
        self.scheduler.start()
        self.is_running = True

        # Perform initial sync
        await self._sync_calendar()

        logger.info("✅ Calendar scheduler started successfully")

    async def stop(self):
        """Stop the calendar scheduler."""
        if not self.is_running:
            return

        logger.info("Stopping calendar scheduler...")

        # Shutdown scheduler
        if self.scheduler:
            self.scheduler.shutdown(wait=False)
            self.scheduler = None

        # Disconnect CalDAV
        if self.caldav_client:
            self.caldav_client.disconnect()
            self.caldav_client = None

        self.is_running = False
        logger.info("Calendar scheduler stopped")

    async def _sync_calendar(self):
        """Sync calendar events from CalDAV server."""
        if not self.caldav_client:
            logger.error("CalDAV client not initialized")
            return

        try:
            logger.info("Syncing calendar events...")

            # Fetch events for next 24 hours
            start_date = datetime.now()
            end_date = start_date + timedelta(hours=24)

            events = await asyncio.to_thread(
                self.caldav_client.fetch_events,
                start_date,
                end_date
            )

            # Filter for BBB meetings only
            bbb_meetings = [event for event in events if event.bbb_url]

            self.upcoming_meetings = bbb_meetings
            self.last_sync = datetime.now()

            logger.info(
                f"✅ Calendar sync complete: {len(events)} total events, "
                f"{len(bbb_meetings)} BBB meetings"
            )

            # Log upcoming meetings
            for event in bbb_meetings:
                time_until = event.time_until_start
                logger.info(
                    f"  📅 {event.summary} - "
                    f"Starts in {time_until.total_seconds() / 60:.0f} minutes"
                )

        except Exception as e:
            logger.error(f"Failed to sync calendar: {e}", exc_info=True)

    async def _check_upcoming_meetings(self):
        """Check if any meetings should be joined now."""
        if not self.config.auto_join_enabled:
            return

        if not self.upcoming_meetings:
            return

        now = datetime.now()
        join_threshold_minutes = self.config.join_before_minutes

        for event in self.upcoming_meetings:
            # Skip if already joined
            if event.uid in self.joined_meetings:
                continue

            # Check if meeting should be joined
            time_until = event.time_until_start
            minutes_until = time_until.total_seconds() / 60

            # Join if within threshold
            if 0 <= minutes_until <= join_threshold_minutes:
                logger.info(
                    f"🚀 Auto-joining meeting: {event.summary} "
                    f"(starts in {minutes_until:.1f} minutes)"
                )

                # Trigger meeting join
                await self._join_meeting(event)

                # Mark as joined
                self.joined_meetings[event.uid] = event

            # Clean up past meetings
            elif time_until.total_seconds() < -3600:  # 1 hour past
                logger.debug(f"Removing past meeting: {event.summary}")
                self.upcoming_meetings.remove(event)
                if event.uid in self.joined_meetings:
                    del self.joined_meetings[event.uid]

    async def _join_meeting(self, event: MeetingEvent):
        """
        Join a meeting from calendar event.

        Args:
            event: Meeting event to join
        """
        if not self.on_meeting_start:
            logger.warning(
                f"No meeting join callback configured for: {event.summary}"
            )
            return

        try:
            logger.info(f"Joining calendar meeting: {event.summary}")
            logger.info(f"  URL: {event.bbb_url}")
            logger.info(f"  Start: {event.start_time}")
            logger.info(f"  End: {event.end_time}")

            # Call the join callback
            await self.on_meeting_start(event)

            logger.info(f"✅ Successfully joined meeting: {event.summary}")

        except Exception as e:
            logger.error(
                f"Failed to join meeting '{event.summary}': {e}",
                exc_info=True
            )

    def get_next_meeting(self) -> Optional[MeetingEvent]:
        """
        Get the next upcoming meeting.

        Returns:
            Next MeetingEvent or None if no meetings scheduled
        """
        if not self.upcoming_meetings:
            return None

        # Sort by start time
        sorted_meetings = sorted(
            self.upcoming_meetings,
            key=lambda e: e.start_time
        )

        # Return first upcoming meeting
        now = datetime.now()
        for meeting in sorted_meetings:
            if meeting.start_time > now:
                return meeting

        return None

    def get_current_meetings(self) -> List[MeetingEvent]:
        """
        Get all currently active meetings.

        Returns:
            List of active MeetingEvent objects
        """
        now = datetime.now()
        return [
            event for event in self.upcoming_meetings
            if event.start_time <= now <= event.end_time
        ]

    def get_status(self) -> Dict[str, any]:
        """
        Get scheduler status information.

        Returns:
            Dictionary with status details
        """
        next_meeting = self.get_next_meeting()
        current_meetings = self.get_current_meetings()

        status = {
            "running": self.is_running,
            "caldav_enabled": self.config.enabled,
            "auto_join_enabled": self.config.auto_join_enabled,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "upcoming_meetings_count": len(self.upcoming_meetings),
            "joined_meetings_count": len(self.joined_meetings),
            "current_meetings_count": len(current_meetings),
            "next_meeting": {
                "summary": next_meeting.summary,
                "start_time": next_meeting.start_time.isoformat(),
                "time_until_start_minutes": next_meeting.time_until_start.total_seconds() / 60,
                "bbb_url": next_meeting.bbb_url,
            } if next_meeting else None,
            "sync_interval_minutes": self.config.sync_interval_minutes,
            "check_interval_seconds": self.config.check_interval_seconds,
        }

        return status

    async def force_sync(self):
        """Manually trigger a calendar sync."""
        logger.info("Manual calendar sync requested")
        await self._sync_calendar()

    def add_mock_meeting(
        self,
        summary: str,
        bbb_url: str,
        start_time: datetime,
        duration_minutes: int = 60,
        password: Optional[str] = None
    ) -> MeetingEvent:
        """
        Add a mock meeting for testing (only works with MockCalDAVClient).

        Args:
            summary: Meeting title
            bbb_url: BigBlueButton room URL
            start_time: Meeting start time
            duration_minutes: Meeting duration
            password: Optional BBB room password

        Returns:
            Created MeetingEvent
        """
        if not self.use_mock:
            raise RuntimeError("Mock meetings only available in mock mode")

        from src.orchestrator.calendar_sync import MockCalDAVClient

        if not isinstance(self.caldav_client, MockCalDAVClient):
            raise RuntimeError("CalDAV client is not a mock client")

        event = MeetingEvent(
            uid=f"mock-{datetime.now().timestamp()}",
            summary=summary,
            description=f"Mock meeting created for testing\n\nJoin: {bbb_url}",
            start_time=start_time,
            end_time=start_time + timedelta(minutes=duration_minutes),
            location=bbb_url,
            bbb_url=bbb_url,
            bbb_password=password,
        )

        self.caldav_client.add_mock_event(event)
        logger.info(f"Added mock meeting: {summary}")

        return event
