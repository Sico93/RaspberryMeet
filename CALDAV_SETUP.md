# CalDAV Calendar Integration Setup Guide

**RaspberryMeet** - Automatic BigBlueButton Meeting Joins from Calendar Events

---

## Table of Contents

1. [Overview](#overview)
2. [Supported CalDAV Servers](#supported-caldav-servers)
3. [Nextcloud Setup](#nextcloud-setup)
4. [Radicale Setup](#radicale-setup)
5. [RaspberryMeet Configuration](#raspberrymeet-configuration)
6. [Creating Calendar Events](#creating-calendar-events)
7. [Testing Calendar Sync](#testing-calendar-sync)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)

---

## Overview

CalDAV integration enables RaspberryMeet to:

- **Automatically sync** calendar events from Nextcloud, Radicale, or other CalDAV servers
- **Detect BigBlueButton meetings** in calendar event descriptions
- **Auto-join meetings** at the scheduled time (configurable lead time)
- **Privacy-first** - all data stays in EU (no Google Calendar, no Microsoft 365)

### How It Works

1. **Calendar Sync**: RaspberryMeet connects to your CalDAV server every 5 minutes (configurable)
2. **Meeting Detection**: Scans event descriptions for BBB meeting URLs
3. **Auto-Join**: Joins meetings automatically 2 minutes before start time (configurable)
4. **Browser Automation**: Opens BBB URL in kiosk browser and handles join flow

---

## Supported CalDAV Servers

RaspberryMeet supports any standards-compliant CalDAV server:

### ✅ Recommended (EU-Based, Privacy-Friendly)

| Server | Type | Hosting | Difficulty | Notes |
|--------|------|---------|------------|-------|
| **Nextcloud** | Full groupware | Self-hosted or managed | Easy | Best all-in-one solution |
| **Radicale** | Minimal CalDAV | Self-hosted | Easy | Lightweight, Python-based |
| **Baikal** | CalDAV/CardDAV | Self-hosted | Easy | Simple PHP app |
| **SOGo** | Enterprise groupware | Self-hosted | Medium | For larger organizations |

### ❌ Not Recommended (Privacy Concerns)

- **Google Calendar** - USA-based, data mining, privacy issues
- **Microsoft 365 / Outlook** - USA-based, corporate surveillance
- **iCloud Calendar** - USA-based, Apple ecosystem lock-in

---

## Nextcloud Setup

Nextcloud is the recommended CalDAV server for RaspberryMeet.

### Step 1: Install Nextcloud

**Option A: Managed Hosting (Easiest)**

Choose a European Nextcloud provider:
- **Hetzner** (Germany): https://www.hetzner.com/de/storage/storage-share
- **IONOS** (Germany): https://www.ionos.de/hosting/nextcloud-hosting
- **Tab Digital** (Switzerland): https://nextcloud.tab.digital/

**Option B: Self-Hosted**

```bash
# Docker Compose method (recommended)
version: '3'

services:
  nextcloud:
    image: nextcloud:latest
    ports:
      - 8080:80
    volumes:
      - nextcloud_data:/var/www/html
    environment:
      - MYSQL_HOST=db
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=secure-password

  db:
    image: mariadb:10.6
    volumes:
      - db_data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=root-password
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=secure-password

volumes:
  nextcloud_data:
  db_data:
```

Save as `docker-compose.yml` and run:

```bash
docker-compose up -d
```

Access Nextcloud at `http://your-server-ip:8080`

### Step 2: Create Nextcloud User for RaspberryMeet

1. **Login to Nextcloud** as admin
2. **Navigate to** Users > Add user
3. **Create user**:
   - Username: `meetingroom1` (or descriptive name)
   - Display name: `Meeting Room 1`
   - Password: Generate strong password
   - Groups: (optional) Create "Meeting Rooms" group

4. **Grant calendar permissions**:
   - Login as the new user
   - Open **Calendar** app
   - Create calendar named "Meetings"

### Step 3: Generate App Password (Recommended)

Using app passwords instead of main password improves security.

1. **Login** as the meeting room user
2. **Settings** > **Security**
3. **App passwords** > **Create new app password**
4. **Name**: `RaspberryMeet`
5. **Copy the generated password** - you'll need this for `.env`

### Step 4: Get CalDAV URL

Nextcloud CalDAV URL format:

```
https://your-nextcloud.com/remote.php/dav
```

Examples:
- Managed hosting: `https://nextcloud.example.eu/remote.php/dav`
- Self-hosted: `https://cloud.yourcompany.de/remote.php/dav`
- Local network: `http://192.168.1.100:8080/remote.php/dav`

---

## Radicale Setup

Radicale is a minimal, lightweight CalDAV server perfect for small deployments.

### Step 1: Install Radicale

**Docker method:**

```bash
docker run -d \
  --name radicale \
  -p 5232:5232 \
  -v radicale_data:/data \
  tomsquest/docker-radicale:latest
```

**Python pip method:**

```bash
# Install
pip install radicale

# Create config
mkdir -p ~/.config/radicale
cat > ~/.config/radicale/config <<EOF
[server]
hosts = 0.0.0.0:5232

[auth]
type = htpasswd
htpasswd_filename = /path/to/users
htpasswd_encryption = bcrypt

[storage]
filesystem_folder = /path/to/collections
EOF

# Create user
htpasswd -B -c /path/to/users meetingroom1

# Run
python -m radicale
```

### Step 2: Configure Radicale

1. **Create calendar collection**:

```bash
# Use a CalDAV client or curl
curl -u meetingroom1:password \
  -X MKCALENDAR \
  http://localhost:5232/meetingroom1/meetings.ics/
```

2. **CalDAV URL format**:

```
http://your-server:5232/username/
```

Example: `http://192.168.1.100:5232/meetingroom1/`

---

## RaspberryMeet Configuration

### Step 1: Configure Environment Variables

Edit `/home/pi/RaspberryMeet/.env`:

```bash
# CalDAV Calendar Integration
CALDAV_ENABLED=true

# Nextcloud example
CALDAV_URL=https://nextcloud.example.eu/remote.php/dav
CALDAV_USERNAME=meetingroom1
CALDAV_PASSWORD=your-app-password-here

# Radicale example
# CALDAV_URL=http://192.168.1.100:5232/meetingroom1/
# CALDAV_USERNAME=meetingroom1
# CALDAV_PASSWORD=your-password

# Calendar name
CALDAV_CALENDAR_NAME=Meetings

# Sync interval (how often to check for new events)
CALDAV_SYNC_INTERVAL_MINUTES=5

# Auto-join settings
CALDAV_AUTO_JOIN_ENABLED=true
# Join meeting X minutes before scheduled start
CALDAV_JOIN_BEFORE_MINUTES=2
# Check for upcoming meetings every X seconds
CALDAV_CHECK_INTERVAL_SECONDS=30
```

### Step 2: Install CalDAV Dependencies

```bash
cd /home/pi/RaspberryMeet
source venv/bin/activate
pip install caldav icalendar vobject APScheduler
```

(These should already be in `requirements.txt`)

### Step 3: Test Connection

```bash
python scripts/test_calendar.py
```

Expected output:

```
====================================================================
  Test 1: Mock CalDAV Client
====================================================================

✅ Created mock CalDAV client
✅ Connected to mock server
✅ Added 3 mock events

📋 Fetched 3 events:

📅 Team Standup
   Start: 2025-11-19 10:00:00
   ...
```

---

## Creating Calendar Events

### Event Format for Auto-Join

RaspberryMeet detects BBB meetings by scanning event descriptions for URLs.

**Required:** BigBlueButton URL in description or location field

**Optional:** Password in description

### Example 1: Simple BBB Meeting

**Event Details:**
- **Title**: Team Standup
- **Start**: 2025-11-19 10:00
- **End**: 2025-11-19 10:30
- **Description**:
  ```
  Daily team standup meeting.

  Join BigBlueButton:
  https://bbb.example.com/b/team-standup
  ```

### Example 2: Password-Protected Meeting

**Event Details:**
- **Title**: Client Presentation
- **Start**: 2025-11-19 14:00
- **End**: 2025-11-19 15:00
- **Description**:
  ```
  Q4 planning with client.

  BigBlueButton: https://bbb.example.com/b/client-q4
  Password: secure123
  ```

### Example 3: Using Location Field

**Event Details:**
- **Title**: Board Meeting
- **Start**: 2025-11-20 09:00
- **End**: 2025-11-20 11:00
- **Location**: `https://bbb.example.com/b/board-meeting`
- **Description**: Monthly board meeting

### Supported URL Patterns

RaspberryMeet recognizes these BBB URL formats:

```
https://bbb.example.com/b/room-name
https://bbb.example.com/bigbluebutton/join?...
https://example.com/conference/room123
http://192.168.1.50/b/meeting-room
```

### Supported Password Patterns

```
Password: secret123
Passwort: geheim456
PIN: 1234
Access code: 5678
```

---

## Testing Calendar Sync

### Manual Test with Mock Events

```bash
cd /home/pi/RaspberryMeet
python scripts/test_calendar.py
```

This runs comprehensive tests:
1. Mock CalDAV client with test events
2. Real CalDAV server connection (if configured)
3. Auto-join scheduler simulation

### Create Test Event in Calendar

1. **Login to Nextcloud/Radicale**
2. **Create new event**:
   - Title: "Test Auto-Join"
   - Start: 5 minutes from now
   - Description: `Test meeting\n\nhttps://bbb.example.com/b/test-room`
3. **Save event**

4. **Monitor RaspberryMeet logs**:

```bash
journalctl -u raspberrymeet -f
```

Expected log output:

```
[INFO] Syncing calendar events...
[INFO] ✅ Calendar sync complete: 1 total events, 1 BBB meetings
[INFO]   📅 Test Auto-Join - Starts in 4 minutes
[INFO] 🚀 Auto-joining meeting: Test Auto-Join (starts in 1.8 minutes)
[INFO] Joining meeting: https://bbb.example.com/b/test-room
[INFO] ✅ Successfully joined meeting
```

### Check System Status

```bash
# Via web interface
http://raspberrypi.local:8080

# Or via API
curl http://raspberrypi.local:8080/api/status | jq '.calendar'
```

Response:

```json
{
  "calendar": {
    "running": true,
    "caldav_enabled": true,
    "auto_join_enabled": true,
    "last_sync": "2025-11-19T09:55:00",
    "upcoming_meetings_count": 3,
    "next_meeting": {
      "summary": "Team Standup",
      "start_time": "2025-11-19T10:00:00",
      "time_until_start_minutes": 4.2,
      "bbb_url": "https://bbb.example.com/b/team-standup"
    }
  }
}
```

---

## Troubleshooting

### Connection Issues

**Problem**: `Failed to connect to CalDAV server`

**Solutions**:

1. **Check URL format**:
   ```bash
   # Nextcloud
   CALDAV_URL=https://nextcloud.example.com/remote.php/dav
   # NOT: https://nextcloud.example.com (missing path)
   ```

2. **Test with curl**:
   ```bash
   curl -u username:password \
     https://nextcloud.example.com/remote.php/dav/calendars/username/
   ```

3. **Check firewall**:
   ```bash
   # On server
   sudo ufw allow 443/tcp

   # On Raspberry Pi
   ping nextcloud.example.com
   ```

4. **Verify credentials**:
   - Try logging into Nextcloud web interface
   - Regenerate app password
   - Check for typos in `.env`

### No Events Found

**Problem**: Calendar sync succeeds but no events detected

**Solutions**:

1. **Check calendar name**:
   ```bash
   # List all calendars
   python -c "
   from src.orchestrator.calendar_sync import create_caldav_client
   from dotenv import load_dotenv
   import os

   load_dotenv()
   client = create_caldav_client(
       os.getenv('CALDAV_URL'),
       os.getenv('CALDAV_USERNAME'),
       os.getenv('CALDAV_PASSWORD')
   )
   client.connect()
   for cal in client.calendars:
       print(f'Calendar: {cal.name}')
   "
   ```

2. **Check event time range**:
   - Events are fetched for next 24 hours only
   - Create an event starting within 1 hour

3. **Verify BBB URL format**:
   - Must be `https://` or `http://`
   - Must be in description or location field
   - Check logs for "No BBB URL found" warnings

### Auto-Join Not Triggering

**Problem**: Events detected but meeting doesn't auto-join

**Solutions**:

1. **Check auto-join enabled**:
   ```bash
   grep CALDAV_AUTO_JOIN_ENABLED .env
   # Should be: CALDAV_AUTO_JOIN_ENABLED=true
   ```

2. **Check lead time**:
   ```bash
   # Join 2 minutes before start
   CALDAV_JOIN_BEFORE_MINUTES=2

   # Event must be within this window
   # If event starts at 10:00, auto-join triggers at 09:58
   ```

3. **Check system state**:
   ```bash
   curl http://localhost:8080/api/status | jq '.state'
   ```
   - Must be `"idle"` to auto-join
   - If `"active"`, leave current meeting first

4. **Check logs**:
   ```bash
   journalctl -u raspberrymeet -f | grep -i "auto-join"
   ```

### SSL Certificate Errors

**Problem**: `SSL: CERTIFICATE_VERIFY_FAILED`

**Solutions**:

1. **Use proper HTTPS** (recommended):
   ```bash
   # Install Let's Encrypt on Nextcloud server
   sudo certbot --nginx -d nextcloud.example.com
   ```

2. **For local testing only** (insecure):
   ```python
   # In calendar_sync.py, add:
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context
   ```

   ⚠️ **Never use in production!**

---

## Advanced Configuration

### Multiple Calendars

Sync multiple calendars by leaving `CALDAV_CALENDAR_NAME` empty:

```bash
# Sync all calendars
CALDAV_CALENDAR_NAME=
```

Or specify one:

```bash
# Sync only "Meetings" calendar
CALDAV_CALENDAR_NAME=Meetings
```

### Custom Sync Intervals

Adjust based on your needs:

```bash
# More frequent sync (every 1 minute)
CALDAV_SYNC_INTERVAL_MINUTES=1

# Less frequent (every 15 minutes, save bandwidth)
CALDAV_SYNC_INTERVAL_MINUTES=15

# Check for upcoming meetings more often
CALDAV_CHECK_INTERVAL_SECONDS=15
```

### Longer Auto-Join Lead Time

Join meetings earlier:

```bash
# Join 5 minutes before start
CALDAV_JOIN_BEFORE_MINUTES=5

# Join 10 minutes before (for slow networks)
CALDAV_JOIN_BEFORE_MINUTES=10
```

### Disable Auto-Join (Manual Only)

Keep calendar sync but require manual join:

```bash
CALDAV_ENABLED=true
CALDAV_AUTO_JOIN_ENABLED=false
```

Events will appear in web interface but won't auto-join.

### Read-Only Calendar Access

Create a shared calendar in Nextcloud:

1. **Create calendar** as main user
2. **Share** with meeting room user
3. **Permissions**: Read-only
4. **Configure RaspberryMeet** to sync this calendar

Benefits:
- Centralized calendar management
- Meeting room can't modify events
- Multiple rooms can share calendar

### Event Filters

Coming soon: Filter events by:
- Attendee (only join if room is invited)
- Category (only join "Video Conference" category)
- Custom fields

---

## Security Best Practices

### 1. Use App Passwords

Never use main Nextcloud password:

```bash
# Generate app password in Nextcloud
Settings > Security > App passwords > Create new

# Use app password in .env
CALDAV_PASSWORD=xHk9p-4mQR2-tY7sL-nB3cV
```

### 2. HTTPS Only

Always use encrypted connections:

```bash
# Good
CALDAV_URL=https://nextcloud.example.com/remote.php/dav

# Bad (insecure)
# CALDAV_URL=http://nextcloud.example.com/remote.php/dav
```

### 3. Restrict Network Access

Limit CalDAV server access:

```bash
# Firewall rule (Nextcloud server)
sudo ufw allow from 192.168.1.0/24 to any port 443
sudo ufw deny 443
```

### 4. Dedicated User Account

Use separate Nextcloud user for each meeting room:

- `meetingroom1@company.com`
- `meetingroom2@company.com`

Don't share accounts between rooms.

### 5. Rotate Passwords

Change app passwords periodically:

```bash
# Revoke old password in Nextcloud
# Generate new password
# Update .env
# Restart service
sudo systemctl restart raspberrymeet
```

---

## Privacy Considerations

### Why CalDAV Instead of Google Calendar?

| Feature | CalDAV (Nextcloud) | Google Calendar |
|---------|-------------------|-----------------|
| **Data location** | EU (self-hosted) | USA (Google servers) |
| **Privacy** | Full control | Data mining, ad targeting |
| **GDPR compliance** | ✅ Yes | ⚠️ Questionable |
| **Vendor lock-in** | ❌ None (open standard) | ✅ Yes (proprietary API) |
| **Cost** | Free (self-hosted) | Free (with your data) |

### GDPR Compliance

When using RaspberryMeet with CalDAV:

1. **Data minimization**: Only calendar events are synced
2. **Purpose limitation**: Data used only for meeting joins
3. **Storage limitation**: Events cached locally, deleted after meeting ends
4. **EU hosting**: Use EU-based CalDAV servers
5. **Access control**: Dedicated user accounts per meeting room

### Data Flow

```
Nextcloud (EU) → CalDAV (HTTPS) → RaspberryMeet (Local) → BBB Meeting
    ↑                                    ↑                      ↑
  GDPR                              No cloud              Self-hosted
compliant                          dependency             or EU-based
```

No data leaves EU if both Nextcloud and BBB are EU-hosted.

---

## Calendar Client Recommendations

For creating/managing events, use:

**Desktop:**
- **Thunderbird** (Free, open source) + Lightning calendar
- **Evolution** (Linux)
- **Nextcloud web interface**

**Mobile:**
- **DAVx⁵** (Android, F-Droid) + any calendar app
- **Nextcloud app** (Android/iOS)

**Avoid:**
- Proprietary cloud calendar apps
- Apps that sync with Google/Apple

---

## Appendix: Example Event Templates

### Template 1: Recurring Daily Standup

```
Title: Daily Standup
Recurrence: Every weekday at 09:00
Duration: 15 minutes
Description:
  Daily team synchronization.

  Join BBB: https://bbb.company.eu/b/daily-standup
```

### Template 2: Weekly Team Meeting

```
Title: Weekly Team Meeting
Recurrence: Every Monday at 14:00
Duration: 1 hour
Description:
  Weekly planning and status updates.

  BigBlueButton: https://bbb.company.eu/b/team-weekly
  Password: team2024

  Agenda:
  - Sprint review
  - Next week planning
  - Open discussion
```

### Template 3: Client Call

```
Title: Client ABC - Project Review
Start: 2025-11-20 10:00
Duration: 2 hours
Location: https://bbb.company.eu/b/client-abc
Description:
  Quarterly project review with Client ABC.

  Access Code: abc2024

  Attendees:
  - Project Manager
  - Technical Lead
  - Client stakeholders
```

---

## Further Reading

- **CalDAV Protocol**: https://datatracker.ietf.org/doc/html/rfc4791
- **Nextcloud Documentation**: https://docs.nextcloud.com/
- **Radicale Documentation**: https://radicale.org/documentation/
- **BigBlueButton API**: https://docs.bigbluebutton.org/dev/api.html

---

**Last Updated**: 2025-11-19
**RaspberryMeet Version**: 1.0.0

For issues or questions, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open an issue on GitHub.
