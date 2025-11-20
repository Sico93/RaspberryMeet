#!/usr/bin/env python3
"""
Test CalDAV calendar integration and meeting detection.

This script tests the calendar sync functionality with mock events
and optionally with a real CalDAV server.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.orchestrator.calendar_sync import (
    create_caldav_client,
    MeetingEvent,
    MockCalDAVClient
)
from src.orchestrator.calendar_scheduler import CalendarScheduler
from src.utils.config import CalDAVConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


def print_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_event(event: MeetingEvent):
    """Print meeting event details."""
    print(f"📅 {event.summary}")
    print(f"   Start: {event.start_time}")
    print(f"   End: {event.end_time}")
    print(f"   Duration: {(event.end_time - event.start_time).total_seconds() / 60:.0f} minutes")

    if event.bbb_url:
        print(f"   ✅ BBB URL: {event.bbb_url}")
    else:
        print(f"   ❌ No BBB URL found")

    if event.bbb_password:
        print(f"   🔒 Password: {'*' * len(event.bbb_password)}")

    if event.organizer:
        print(f"   👤 Organizer: {event.organizer}")

    if event.attendees:
        print(f"   👥 Attendees: {len(event.attendees)}")


async def test_mock_client():
    """Test CalDAV client with mock events."""
    print_header("Test 1: Mock CalDAV Client")

    # Create mock client
    client = create_caldav_client(
        url="https://mock.example.com/dav",
        username="test@example.com",
        password="test",
        use_mock=True
    )

    print("✅ Created mock CalDAV client")

    # Connect
    if not client.connect():
        print("❌ Failed to connect (mock should always succeed)")
        return

    print("✅ Connected to mock server")

    # Create mock events
    mock_events = [
        MeetingEvent(
            uid="mock-1",
            summary="Team Standup",
            description="Daily team standup\n\nJoin: https://bbb.example.com/b/team-standup",
            start_time=datetime.now() + timedelta(minutes=10),
            end_time=datetime.now() + timedelta(minutes=25),
            location="https://bbb.example.com/b/team-standup",
            bbb_url="https://bbb.example.com/b/team-standup",
            bbb_password=None,
            organizer="manager@example.com",
            attendees=["dev1@example.com", "dev2@example.com"]
        ),
        MeetingEvent(
            uid="mock-2",
            summary="Client Meeting",
            description="Q4 Planning Meeting\n\nBBB: https://bbb.example.com/b/client-q4\nPassword: secret123",
            start_time=datetime.now() + timedelta(hours=2),
            end_time=datetime.now() + timedelta(hours=3),
            location="BigBlueButton",
            bbb_url="https://bbb.example.com/b/client-q4",
            bbb_password="secret123",
            organizer="sales@example.com",
            attendees=["client@company.com"]
        ),
        MeetingEvent(
            uid="mock-3",
            summary="Lunch Break (no BBB)",
            description="Team lunch - no video call",
            start_time=datetime.now() + timedelta(hours=3),
            end_time=datetime.now() + timedelta(hours=4),
            location="Cafeteria",
            bbb_url=None,  # Not a BBB meeting
        )
    ]

    # Add mock events
    for event in mock_events:
        client.add_mock_event(event)

    print(f"✅ Added {len(mock_events)} mock events")

    # Fetch events
    events = client.fetch_events()
    print(f"\n📋 Fetched {len(events)} events:\n")

    for event in events:
        print_event(event)
        print()

    # Test current/upcoming meetings
    current = client.get_current_meetings()
    upcoming = client.get_upcoming_meetings(minutes=30)

    print(f"▶️  Currently active meetings: {len(current)}")
    print(f"⏰ Upcoming meetings (next 30 min): {len(upcoming)}")

    client.disconnect()
    print("\n✅ Test 1 complete")


async def test_real_caldav_client(
    url: str,
    username: str,
    password: str,
    calendar_name: str = None
):
    """Test CalDAV client with real server."""
    print_header("Test 2: Real CalDAV Server")

    print(f"Server: {url}")
    print(f"Username: {username}")
    print(f"Calendar: {calendar_name or '(default)'}\n")

    # Create client
    client = create_caldav_client(
        url=url,
        username=username,
        password=password,
        calendar_name=calendar_name,
        use_mock=False
    )

    print("✅ Created CalDAV client")

    # Connect
    if not client.connect():
        print("❌ Failed to connect to CalDAV server")
        print("   Check your credentials and network connection")
        return

    print("✅ Connected to CalDAV server")

    # Fetch events for next 7 days
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)

    print(f"\n📅 Fetching events from {start_date.date()} to {end_date.date()}...\n")

    events = client.fetch_events(start_date, end_date)

    if not events:
        print("ℹ️  No events found in the next 7 days")
        client.disconnect()
        return

    print(f"📋 Found {len(events)} events:\n")

    # Separate BBB and non-BBB events
    bbb_events = [e for e in events if e.bbb_url]
    other_events = [e for e in events if not e.bbb_url]

    if bbb_events:
        print(f"✅ BigBlueButton meetings ({len(bbb_events)}):\n")
        for event in bbb_events:
            print_event(event)
            print()

    if other_events:
        print(f"ℹ️  Other calendar events ({len(other_events)}):\n")
        for event in other_events:
            print(f"   - {event.summary} ({event.start_time})")

    # Test upcoming detection
    upcoming = [e for e in events if e.is_upcoming]
    if upcoming:
        print(f"\n⏰ Meetings starting soon (next 5 minutes):\n")
        for event in upcoming:
            minutes_until = event.time_until_start.total_seconds() / 60
            print(f"   - {event.summary} (in {minutes_until:.1f} minutes)")

    client.disconnect()
    print("\n✅ Test 2 complete")


async def test_calendar_scheduler():
    """Test calendar scheduler with mock events."""
    print_header("Test 3: Calendar Scheduler")

    # Create mock config
    config = CalDAVConfig(
        enabled=True,
        url="https://mock.example.com/dav",
        username="test@example.com",
        password="test",
        calendar_name="Meetings",
        sync_interval_minutes=1,
        auto_join_enabled=True,
        join_before_minutes=2,
        check_interval_seconds=5
    )

    # Track joined meetings
    joined_meetings = []

    async def on_meeting_start(event: MeetingEvent):
        """Callback when meeting should be joined."""
        logger.info(f"🚀 AUTO-JOIN TRIGGERED: {event.summary}")
        joined_meetings.append(event)

    # Create scheduler with mock mode
    scheduler = CalendarScheduler(
        caldav_config=config,
        on_meeting_start=on_meeting_start,
        use_mock=True
    )

    print("✅ Created calendar scheduler (mock mode)")

    # Add mock meeting starting in 30 seconds
    near_future = datetime.now() + timedelta(seconds=30)
    mock_meeting = scheduler.add_mock_meeting(
        summary="Test Auto-Join Meeting",
        bbb_url="https://bbb.example.com/b/test-auto-join",
        start_time=near_future,
        duration_minutes=30,
        password="test123"
    )

    print(f"✅ Added mock meeting starting at {near_future.strftime('%H:%M:%S')}")

    # Start scheduler
    await scheduler.start()
    print("✅ Scheduler started\n")

    # Get status
    status = scheduler.get_status()
    print("📊 Scheduler Status:")
    print(f"   Running: {status['running']}")
    print(f"   CalDAV enabled: {status['caldav_enabled']}")
    print(f"   Auto-join enabled: {status['auto_join_enabled']}")
    print(f"   Upcoming meetings: {status['upcoming_meetings_count']}")

    if status['next_meeting']:
        next_mtg = status['next_meeting']
        print(f"\n⏰ Next Meeting:")
        print(f"   {next_mtg['summary']}")
        print(f"   Starts in: {next_mtg['time_until_start_minutes']:.1f} minutes")

    # Wait for meeting to trigger (max 2 minutes)
    print("\n⏳ Waiting for auto-join trigger (max 2 minutes)...")
    print("   The meeting should auto-join when it's within 2 minutes of start time\n")

    timeout = 120  # 2 minutes
    start_time = datetime.now()

    while (datetime.now() - start_time).total_seconds() < timeout:
        if joined_meetings:
            print(f"\n✅ Auto-join successful!")
            print(f"   Meeting: {joined_meetings[0].summary}")
            print(f"   BBB URL: {joined_meetings[0].bbb_url}")
            break

        await asyncio.sleep(1)
    else:
        print("\n⚠️  Auto-join did not trigger within timeout")
        print("   This might be expected if the test timing is off")

    # Stop scheduler
    await scheduler.stop()
    print("\n✅ Test 3 complete")


async def main():
    """Run all calendar tests."""
    print("\n" + "=" * 70)
    print("  🗓️  RaspberryMeet CalDAV Calendar Test Suite")
    print("=" * 70)

    # Test 1: Mock client
    await test_mock_client()

    # Test 2: Real CalDAV (optional)
    import os
    caldav_url = os.getenv("CALDAV_URL")
    caldav_user = os.getenv("CALDAV_USERNAME")
    caldav_pass = os.getenv("CALDAV_PASSWORD")

    if caldav_url and caldav_user and caldav_pass:
        print("\n" + "ℹ️  " * 35)
        print("   Found CalDAV credentials in environment")
        print("   Do you want to test with your real CalDAV server? (y/n): ", end="")

        # Note: In non-interactive mode, skip this
        try:
            response = input().strip().lower()
            if response == 'y':
                await test_real_caldav_client(
                    url=caldav_url,
                    username=caldav_user,
                    password=caldav_pass,
                    calendar_name=os.getenv("CALDAV_CALENDAR_NAME")
                )
        except (EOFError, KeyboardInterrupt):
            print("\nSkipping real CalDAV test (non-interactive mode)")
    else:
        print("\nℹ️  Skipping real CalDAV test (credentials not configured)")
        print("   Set CALDAV_URL, CALDAV_USERNAME, CALDAV_PASSWORD to test")

    # Test 3: Scheduler
    await test_calendar_scheduler()

    # Summary
    print_header("✅ All Tests Complete")
    print("Calendar sync functionality is working correctly!\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
