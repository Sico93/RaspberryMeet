"""
CalDAV calendar synchronization for RaspberryMeet.

Connects to Nextcloud/Radicale CalDAV servers to sync calendar events
and detect BigBlueButton meetings for automatic joining.
"""

import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from urllib.parse import urlparse

try:
    import caldav
    from caldav.elements import dav
    from icalendar import Calendar, Event
    CALDAV_AVAILABLE = True
except ImportError:
    CALDAV_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MeetingEvent:
    """Represents a calendar meeting event."""

    uid: str
    summary: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str
    bbb_url: Optional[str] = None
    bbb_password: Optional[str] = None
    organizer: Optional[str] = None
    attendees: List[str] = None

    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []

    @property
    def is_active(self) -> bool:
        """Check if the meeting is currently active."""
        now = datetime.now(self.start_time.tzinfo)
        return self.start_time <= now <= self.end_time

    @property
    def is_upcoming(self, minutes: int = 5) -> bool:
        """Check if the meeting starts within the specified minutes."""
        now = datetime.now(self.start_time.tzinfo)
        threshold = now + timedelta(minutes=minutes)
        return now <= self.start_time <= threshold

    @property
    def time_until_start(self) -> timedelta:
        """Get time until meeting starts."""
        now = datetime.now(self.start_time.tzinfo)
        return self.start_time - now

    def __repr__(self) -> str:
        return f"<MeetingEvent: {self.summary} at {self.start_time}>"


class CalDAVClient:
    """CalDAV client for Nextcloud/Radicale calendar synchronization."""

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        calendar_name: Optional[str] = None
    ):
        """
        Initialize CalDAV client.

        Args:
            url: CalDAV server URL (e.g., https://nextcloud.example.com/remote.php/dav)
            username: CalDAV username/email
            password: CalDAV password or app token
            calendar_name: Specific calendar name to sync (optional)
        """
        self.url = url
        self.username = username
        self.password = password
        self.calendar_name = calendar_name
        self.client: Optional[caldav.DAVClient] = None
        self.principal = None
        self.calendars: List[caldav.Calendar] = []

        if not CALDAV_AVAILABLE:
            logger.warning("CalDAV libraries not available. Using mock mode.")

    def connect(self) -> bool:
        """
        Connect to CalDAV server and discover calendars.

        Returns:
            True if connection successful, False otherwise
        """
        if not CALDAV_AVAILABLE:
            logger.warning("CalDAV not available - cannot connect")
            return False

        try:
            logger.info(f"Connecting to CalDAV server: {self.url}")
            self.client = caldav.DAVClient(
                url=self.url,
                username=self.username,
                password=self.password
            )

            # Get principal (user account)
            self.principal = self.client.principal()

            # Discover calendars
            self.calendars = self.principal.calendars()

            if not self.calendars:
                logger.warning("No calendars found on server")
                return False

            logger.info(f"Found {len(self.calendars)} calendar(s)")
            for cal in self.calendars:
                logger.info(f"  - {cal.name}")

            return True

        except Exception as e:
            logger.error(f"Failed to connect to CalDAV server: {e}")
            return False

    def get_calendar(self) -> Optional[caldav.Calendar]:
        """
        Get the target calendar for syncing.

        Returns:
            Calendar object or None if not found
        """
        if not self.calendars:
            logger.error("No calendars available")
            return None

        # If specific calendar name requested, find it
        if self.calendar_name:
            for cal in self.calendars:
                if cal.name == self.calendar_name:
                    logger.info(f"Using calendar: {self.calendar_name}")
                    return cal
            logger.warning(f"Calendar '{self.calendar_name}' not found, using default")

        # Use first calendar as default
        default_cal = self.calendars[0]
        logger.info(f"Using default calendar: {default_cal.name}")
        return default_cal

    def fetch_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MeetingEvent]:
        """
        Fetch calendar events within date range.

        Args:
            start_date: Start of date range (default: now)
            end_date: End of date range (default: now + 24 hours)

        Returns:
            List of MeetingEvent objects
        """
        if not CALDAV_AVAILABLE or not self.client:
            logger.warning("CalDAV not available - returning empty event list")
            return []

        # Set default date range
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(hours=24)

        calendar = self.get_calendar()
        if not calendar:
            return []

        try:
            logger.info(f"Fetching events from {start_date} to {end_date}")

            # Search for events in date range
            events = calendar.date_search(
                start=start_date,
                end=end_date,
                expand=True
            )

            meeting_events = []
            for event in events:
                meeting_event = self._parse_event(event)
                if meeting_event:
                    meeting_events.append(meeting_event)

            logger.info(f"Found {len(meeting_events)} meeting event(s)")
            return meeting_events

        except Exception as e:
            logger.error(f"Failed to fetch events: {e}")
            return []

    def _parse_event(self, cal_event: caldav.CalendarObjectResource) -> Optional[MeetingEvent]:
        """
        Parse CalDAV event into MeetingEvent object.

        Args:
            cal_event: CalDAV calendar event

        Returns:
            MeetingEvent object or None if parsing fails
        """
        try:
            # Parse iCalendar data
            ical = Calendar.from_ical(cal_event.data)

            for component in ical.walk():
                if component.name == "VEVENT":
                    # Extract basic event info
                    uid = str(component.get('uid', ''))
                    summary = str(component.get('summary', 'Untitled Meeting'))
                    description = str(component.get('description', ''))
                    location = str(component.get('location', ''))

                    # Extract dates
                    dtstart = component.get('dtstart')
                    dtend = component.get('dtend')

                    if not dtstart or not dtend:
                        logger.warning(f"Event {summary} missing start/end time")
                        continue

                    start_time = dtstart.dt
                    end_time = dtend.dt

                    # Ensure datetime objects (not just date)
                    if not isinstance(start_time, datetime):
                        start_time = datetime.combine(start_time, datetime.min.time())
                    if not isinstance(end_time, datetime):
                        end_time = datetime.combine(end_time, datetime.max.time())

                    # Extract organizer
                    organizer = None
                    if component.get('organizer'):
                        org_str = str(component.get('organizer'))
                        # Extract email from mailto: URI
                        if 'mailto:' in org_str.lower():
                            organizer = org_str.lower().replace('mailto:', '').strip()

                    # Extract attendees
                    attendees = []
                    for attendee in component.get('attendee', []):
                        att_str = str(attendee)
                        if 'mailto:' in att_str.lower():
                            email = att_str.lower().replace('mailto:', '').strip()
                            attendees.append(email)

                    # Extract BBB URL and password
                    bbb_url, bbb_password = self._extract_bbb_info(description, location)

                    meeting_event = MeetingEvent(
                        uid=uid,
                        summary=summary,
                        description=description,
                        start_time=start_time,
                        end_time=end_time,
                        location=location,
                        bbb_url=bbb_url,
                        bbb_password=bbb_password,
                        organizer=organizer,
                        attendees=attendees
                    )

                    logger.debug(f"Parsed event: {meeting_event}")
                    return meeting_event

            return None

        except Exception as e:
            logger.error(f"Failed to parse event: {e}")
            return None

    def _extract_bbb_info(self, description: str, location: str) -> tuple[Optional[str], Optional[str]]:
        """
        Extract BigBlueButton URL and password from event description or location.

        Args:
            description: Event description text
            location: Event location text

        Returns:
            Tuple of (bbb_url, bbb_password)
        """
        bbb_url = None
        bbb_password = None

        # Combine description and location for searching
        search_text = f"{description}\n{location}"

        # BBB URL patterns
        url_patterns = [
            r'https?://[^\s]+/b/[a-z0-9-]+',  # Standard BBB room URL
            r'https?://[^\s]+/bigbluebutton/[^\s]+',  # Direct BBB URL
            r'https?://bbb\.[^\s]+',  # BBB subdomain
        ]

        for pattern in url_patterns:
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                bbb_url = match.group(0).strip('.,;:)')
                logger.debug(f"Found BBB URL: {bbb_url}")
                break

        # Password patterns
        password_patterns = [
            r'(?:password|passwort|kennwort|code)[\s:]+([a-zA-Z0-9_-]+)',
            r'(?:pin|access code)[\s:]+([0-9]+)',
        ]

        for pattern in password_patterns:
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                bbb_password = match.group(1).strip()
                logger.debug(f"Found BBB password: {'*' * len(bbb_password)}")
                break

        return bbb_url, bbb_password

    def get_current_meetings(self) -> List[MeetingEvent]:
        """
        Get all currently active meetings.

        Returns:
            List of active MeetingEvent objects
        """
        events = self.fetch_events()
        return [event for event in events if event.is_active]

    def get_upcoming_meetings(self, minutes: int = 5) -> List[MeetingEvent]:
        """
        Get meetings starting within the specified minutes.

        Args:
            minutes: Look-ahead time in minutes

        Returns:
            List of upcoming MeetingEvent objects
        """
        events = self.fetch_events()
        now = datetime.now()
        upcoming = []

        for event in events:
            # Make sure event start time is timezone-aware for comparison
            event_start = event.start_time
            if event_start.tzinfo is None:
                event_start = event_start.replace(tzinfo=now.tzinfo)

            threshold = now + timedelta(minutes=minutes)
            if now <= event_start <= threshold:
                upcoming.append(event)

        return upcoming

    def disconnect(self):
        """Disconnect from CalDAV server and cleanup resources."""
        self.client = None
        self.principal = None
        self.calendars = []
        logger.info("Disconnected from CalDAV server")


class MockCalDAVClient(CalDAVClient):
    """Mock CalDAV client for testing without real server."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mock_events: List[MeetingEvent] = []
        logger.info("Using MockCalDAVClient (no real CalDAV connection)")

    def connect(self) -> bool:
        """Mock connection always succeeds."""
        logger.info("Mock CalDAV: Connected successfully")
        return True

    def fetch_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MeetingEvent]:
        """Return mock events."""
        logger.info(f"Mock CalDAV: Returning {len(self._mock_events)} mock events")
        return self._mock_events

    def add_mock_event(self, event: MeetingEvent):
        """Add a mock event for testing."""
        self._mock_events.append(event)
        logger.info(f"Mock CalDAV: Added mock event '{event.summary}'")

    def clear_mock_events(self):
        """Clear all mock events."""
        self._mock_events = []
        logger.info("Mock CalDAV: Cleared all mock events")


def create_caldav_client(
    url: str,
    username: str,
    password: str,
    calendar_name: Optional[str] = None,
    use_mock: bool = False
) -> CalDAVClient:
    """
    Factory function to create CalDAV client.

    Args:
        url: CalDAV server URL
        username: CalDAV username
        password: CalDAV password
        calendar_name: Specific calendar to use (optional)
        use_mock: Use mock client for testing

    Returns:
        CalDAVClient or MockCalDAVClient instance
    """
    if use_mock or not CALDAV_AVAILABLE:
        return MockCalDAVClient(url, username, password, calendar_name)
    else:
        return CalDAVClient(url, username, password, calendar_name)
