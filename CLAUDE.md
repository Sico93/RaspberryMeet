# CLAUDE.md - AI Assistant Guide for RaspberryMeet

**Last Updated:** 2025-11-15
**Repository:** RaspberryMeet
**Author:** Sico93 (sico93@posteo.de)

---

## Project Overview

**RaspberryMeet** is a Raspberry Pi 4-based BigBlueButton client that enables simple, one-button meeting room access without requiring keyboard or mouse interaction. The system provides automated calendar-based meeting joins and manual GPIO button access to a default meeting room.

**Project Description (DE):**
*Ein Meeting Computer, der eine günstige Nachstellung von professionellen Meetingboards abbilden soll.*

**Core Functionality:**
- **One-Button Join:** GPIO button press joins preconfigured BigBlueButton room
- **Calendar Integration:** Automatic meeting joins based on CalDAV calendar invitations
- **Web Admin Interface:** Local network access for remote meeting control and configuration
- **Hands-Free Operation:** No keyboard/mouse required for standard workflows
- **Privacy-First:** Open source components, EU-based hosting (no USA/China services)

**Target Use Case:**
Power on → Join meeting (button/auto) → Conduct conference → Power off

**Project Status:** GREENFIELD - Initial Setup Phase
**Initial Commit:** 64ef5e3 (2025-11-15)
**Current Branch:** claude/claude-md-mi0ls28jefrj31gk-01Fy51p4K9pYPy9KWyM2Uw6R

---

## Current Repository State

### Existing Files
```
/home/user/RaspberryMeet/
├── .git/              # Git repository metadata
├── README.md          # Project description (2 lines)
└── CLAUDE.md          # This file
```

### What Needs to Be Built
This is a brand new project. The following components need to be implemented:
- **Kiosk Application:** Chromium-based browser in kiosk mode for BigBlueButton
- **Meeting Orchestrator:** Python service managing meeting lifecycle and automation
- **GPIO Controller:** Hardware interface for physical buttons/LEDs
- **Calendar Sync:** CalDAV client for privacy-friendly calendar integration
- **Audio/Video Manager:** PulseAudio/ALSA configuration for conference speakerphone
- **Auto-Join Logic:** Automatic meeting detection and browser automation
- **Configuration Management:** Room credentials, BBB server URLs, default meeting settings
- **Web Admin Interface:** Local network web UI for triggering meetings and configuration
- **Systemd Services:** Boot-time initialization and service management

### Hardware Components
- **Raspberry Pi 4** (4GB+ recommended)
- **Conference Speakerphone:** USB or Bluetooth (auto-detected as default audio device)
- **USB Webcam:** Standard V4L2 compatible camera
- **GPIO Buttons:** 1-3 buttons for meeting control (join, leave, mute)
- **Optional LED Indicators:** Status lights for meeting state
- **Display:** HDMI monitor (1080p recommended)
- **Network:** Ethernet preferred for stability

### BigBlueButton Infrastructure
- **BBB Server:** Provided externally (up to 5 rooms available)
- **Default Room:** Password-protected persistent room for instant access
- **Calendar Rooms:** Dynamic meeting joins via CalDAV invitations

---

## Selected Technology Stack

### Core Architecture: Kiosk + Orchestrator Pattern
**Approach:** Similar to PiMeet, but with BigBlueButton instead of Google Meet

**Browser Layer:**
- **Chromium** in kiosk mode (fullscreen, no UI)
- **Selenium/Playwright** for browser automation
- Auto-launch on boot via systemd + X11/Wayland

**Orchestration Layer:**
- **Python 3.11+** for meeting orchestrator service
- **FastAPI** for web admin interface and REST API
- **gpiozero** for GPIO button/LED control
- **caldav** library for CalDAV calendar integration
- **selenium** or **playwright** for browser automation
- **schedule** or **APScheduler** for time-based tasks

**Audio/Video Stack:**
- **PulseAudio** for audio routing and device management
- **v4l2** for webcam configuration
- **bluez** for Bluetooth speakerphone pairing (if needed)
- Conference speakerphone set as default PulseAudio sink/source

**System Services:**
- **systemd** for service management and auto-start
- **Xorg** or **Wayland** for display server
- **openbox** or minimal window manager for X11 session

**Configuration:**
- **YAML/JSON** config files for BBB URLs, credentials, GPIO pins
- **Environment variables** for secrets (BBB passwords, CalDAV credentials)
- **SQLite** for meeting history and state persistence (optional)

### Calendar Integration (Privacy-First)
- **CalDAV Protocol** (open standard, no vendor lock-in)
- Compatible servers:
  - **Nextcloud** (recommended, EU-hostable)
  - **Radicale** (lightweight, self-hosted)
  - **Baikal** (simple CalDAV/CardDAV server)
  - **SOGo** (groupware alternative)
- **NO Google Calendar** (USA-based, privacy concerns)
- **NO Microsoft 365** (USA-based, privacy concerns)

### BigBlueButton Client
**Option 1: Browser Automation (Recommended)**
- Chromium in kiosk mode navigating to BBB URL
- Selenium/Playwright automates:
  - Username entry
  - Password entry (if required)
  - Microphone/camera permission grants
  - "Join Audio" button clicks
- Pros: Native BBB experience, full feature support
- Cons: Fragile to BBB UI changes

**Option 2: Greenlight Integration**
- Use BBB's Greenlight frontend if available
- Simpler URL structure for direct room access
- Can use API tokens for authentication

**Option 3: BBB API Direct**
- Use BigBlueButton API for meeting creation/joins
- Generate signed join URLs programmatically
- Requires API secret from BBB server admin

### Hardware Interface
- **gpiozero** for GPIO control (high-level, clean API)
- **Button events** trigger meeting join/leave actions
- **LED indicators** show meeting state (idle/joining/active/error)
- **Pin assignments** (example):
  - GPIO 17: Join Default Meeting button
  - GPIO 27: Leave Meeting button
  - GPIO 22: Mute/Unmute toggle button
  - GPIO 23: Status LED (green = ready, red = in meeting, blinking = error)

### Data Privacy & Security
- **All open source** components (no proprietary software)
- **EU-based services** where external hosting needed
- **Local-first** architecture (calendar cache, config files)
- **Encrypted credentials** storage (keyring or encrypted config)
- **Network isolation** option (no internet except BBB server)

### Web Admin Interface
- **FastAPI** backend for REST API and web serving
- **Simple HTML/CSS/JS** frontend (no build process)
- **htmx** for interactive updates without JavaScript frameworks
- **Authentication:** Basic Auth initially, JWT tokens later
- **Features:**
  - Trigger meeting joins via web buttons
  - View current meeting status
  - Configure BBB room URLs and credentials
  - View system logs and diagnostics
  - Manual calendar sync trigger

### Container & Deployment
- **NO Docker** (direct install for better hardware access and lower overhead)
- **systemd** for service management
- **Ansible** or **bash scripts** for reproducible deployment
- **SD card image** for fleet deployment (bonus feature, later phase)

---

## Project Structure

```
RaspberryMeet/
├── .github/
│   └── workflows/
│       └── test.yml                    # CI testing pipeline
├── src/
│   ├── orchestrator/                   # Main Python orchestrator service
│   │   ├── __init__.py
│   │   ├── main.py                     # Service entry point
│   │   ├── meeting_manager.py          # Meeting lifecycle management
│   │   ├── browser_controller.py       # Selenium/Playwright automation
│   │   ├── calendar_sync.py            # CalDAV integration
│   │   ├── gpio_handler.py             # Button/LED GPIO control
│   │   ├── audio_manager.py            # PulseAudio device configuration
│   │   └── config.py                   # Configuration management
│   ├── web/                            # Web admin interface
│   │   ├── __init__.py
│   │   ├── api.py                      # FastAPI routes
│   │   ├── auth.py                     # Authentication middleware
│   │   ├── static/                     # Static files (CSS, JS)
│   │   │   ├── style.css
│   │   │   └── app.js
│   │   └── templates/                  # HTML templates
│   │       ├── index.html
│   │       ├── meetings.html
│   │       └── settings.html
│   ├── models/                         # Data models
│   │   ├── __init__.py
│   │   ├── meeting.py                  # Meeting representation
│   │   └── room.py                     # BBB room configuration
│   └── utils/                          # Utility functions
│       ├── __init__.py
│       ├── logger.py                   # Logging configuration
│       └── validators.py               # Input validation
├── tests/
│   ├── unit/
│   │   ├── test_meeting_manager.py
│   │   ├── test_calendar_sync.py
│   │   └── test_gpio_handler.py
│   ├── integration/
│   │   ├── test_bbb_join.py
│   │   └── test_calendar_flow.py
│   └── fixtures/
│       └── sample_calendar.ics
├── config/
│   ├── config.example.yaml             # Example configuration
│   ├── default_meeting.yaml            # Default BBB room settings
│   ├── gpio_pins.yaml                  # GPIO pin assignments
│   └── audio_devices.yaml              # Audio device preferences
├── systemd/
│   ├── raspberrymeet.service           # Main orchestrator service
│   ├── raspberrymeet-web.service       # Web admin interface
│   ├── raspberrymeet-kiosk.service     # Chromium kiosk launcher
│   └── raspberrymeet-setup.service     # One-time setup on boot
├── scripts/
│   ├── install.sh                      # Initial installation script
│   ├── setup_audio.sh                  # Configure PulseAudio
│   ├── setup_display.sh                # Configure X11/kiosk mode
│   ├── pair_bluetooth.sh               # Bluetooth speaker pairing
│   ├── test_hardware.sh                # Hardware test utility
│   └── update.sh                       # Update deployment
├── docs/
│   ├── ARCHITECTURE.md                 # System architecture
│   ├── SETUP.md                        # Installation guide
│   ├── HARDWARE.md                     # Hardware setup & wiring
│   ├── CALDAV_SETUP.md                 # CalDAV server configuration
│   ├── BBB_SERVER.md                   # BigBlueButton server setup
│   ├── TROUBLESHOOTING.md              # Common issues & solutions
│   └── USER_GUIDE.md                   # End-user instructions (DE/EN)
├── hardware/
│   ├── wiring_diagram.png              # GPIO wiring diagram
│   ├── button_schematic.pdf            # Button circuit schematic
│   └── parts_list.md                   # Bill of materials
├── requirements.txt                    # Python production dependencies
├── requirements-dev.txt                # Development dependencies
├── pytest.ini                          # Pytest configuration
├── .env.example                        # Environment variables template
├── .gitignore                          # Git ignore patterns
├── .editorconfig                       # Editor configuration
├── LICENSE                             # Open source license (MIT/GPL)
├── README.md                           # Project overview
├── README.de.md                        # German README
├── CLAUDE.md                           # This file
└── CONTRIBUTING.md                     # Contribution guidelines
```

---

## Development Workflows

### Git Branch Strategy

**Main Branches:**
- `main` - Production-ready code
- `develop` - Integration branch for features

**Feature Branches:**
- Format: `feature/descriptive-name`
- Example: `feature/calendar-integration`
- Merge into: `develop`

**Bug Fix Branches:**
- Format: `bugfix/issue-description`
- Example: `bugfix/gpio-pin-conflict`
- Merge into: `develop` or `main` (for hotfixes)

**Claude AI Branches:**
- Format: `claude/claude-md-<session-id>`
- These are temporary working branches
- Must be pushed with `-u origin <branch-name>`
- **CRITICAL:** Branch must start with 'claude/' and end with matching session ID

**Release Branches:**
- Format: `release/v1.0.0`
- Use semantic versioning

### Commit Message Conventions

Follow conventional commits format:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code formatting (no logic change)
- `refactor` - Code restructuring
- `test` - Adding or updating tests
- `chore` - Build process, dependencies, etc.
- `perf` - Performance improvements
- `ci` - CI/CD changes

**Examples:**
```
feat(api): add meeting room availability endpoint
fix(hardware): resolve GPIO pin numbering conflict
docs(setup): add Raspberry Pi installation guide
```

### Development Setup

1. **Clone Repository:**
   ```bash
   git clone <repository-url>
   cd RaspberryMeet
   ```

2. **Set Up Backend (Python example):**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Set Up Frontend (React example):**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run Development Server:**
   ```bash
   # Backend
   cd backend && uvicorn app.main:app --reload

   # Frontend
   cd frontend && npm run dev
   ```

### Testing Requirements

**Minimum Coverage:** 70% for production code

**Backend Testing:**
- Unit tests: `pytest backend/tests/`
- Integration tests: Test API endpoints with TestClient
- Hardware mocking: Mock GPIO operations for CI/CD

**Frontend Testing:**
- Component tests: Jest + React Testing Library
- E2E tests: Playwright or Cypress (optional)

**Run Tests:**
```bash
# Backend
pytest backend/tests/ --cov=backend/app --cov-report=html

# Frontend
npm test
```

### Code Quality Tools

**Python (Backend):**
- Linter: `ruff` or `flake8`
- Formatter: `black`
- Type checking: `mypy`
- Import sorting: `isort`

**JavaScript (Frontend):**
- Linter: `eslint`
- Formatter: `prettier`

**Pre-commit Hooks:**
```bash
pip install pre-commit
pre-commit install
```

---

## Coding Standards and Conventions

### Python Backend

1. **Style Guide:** Follow PEP 8
2. **Type Hints:** Use type annotations for all functions
3. **Docstrings:** Google-style docstrings for all public functions
4. **Error Handling:** Use try-except blocks, log errors appropriately
5. **Async/Await:** Use async for I/O operations
6. **Configuration:** Use environment variables, never hardcode secrets

**Example:**
```python
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class Meeting(BaseModel):
    """Meeting data model."""
    id: int
    room_id: int
    title: str
    start_time: str
    end_time: str

async def get_meeting_by_id(meeting_id: int) -> Optional[Meeting]:
    """
    Retrieve a meeting by its ID.

    Args:
        meeting_id: The unique identifier of the meeting

    Returns:
        Meeting object if found, None otherwise
    """
    # Implementation here
    pass
```

### JavaScript Frontend

1. **Style Guide:** Follow Airbnb JavaScript Style Guide
2. **Components:** Use functional components with hooks
3. **Naming:** PascalCase for components, camelCase for functions/variables
4. **File Structure:** One component per file
5. **PropTypes:** Use PropTypes or TypeScript for type checking

**Example:**
```javascript
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * Display meeting status for a room
 */
const MeetingCard = ({ meeting, onUpdate }) => {
  const [status, setStatus] = useState('available');

  useEffect(() => {
    // Update status based on meeting time
    updateStatus();
  }, [meeting]);

  const updateStatus = () => {
    // Implementation
  };

  return (
    <div className="meeting-card">
      {/* Component UI */}
    </div>
  );
};

MeetingCard.propTypes = {
  meeting: PropTypes.object.isRequired,
  onUpdate: PropTypes.func.isRequired,
};

export default MeetingCard;
```

### Hardware Code (Raspberry Pi)

1. **GPIO Safety:** Always use try-finally to clean up GPIO pins
2. **Error Handling:** Handle hardware failures gracefully
3. **Mocking:** Provide mock implementations for development without hardware
4. **Documentation:** Document pin mappings and hardware requirements

**Example:**
```python
import RPi.GPIO as GPIO
from typing import Optional

class LEDController:
    """Control LED indicators for room status."""

    def __init__(self, pin: int):
        """
        Initialize LED controller.

        Args:
            pin: GPIO pin number (BCM numbering)
        """
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def turn_on(self) -> None:
        """Turn on the LED."""
        GPIO.output(self.pin, GPIO.HIGH)

    def turn_off(self) -> None:
        """Turn off the LED."""
        GPIO.output(self.pin, GPIO.LOW)

    def cleanup(self) -> None:
        """Clean up GPIO resources."""
        GPIO.cleanup(self.pin)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
```

---

## API Design Conventions

### RESTful Endpoints

Use standard HTTP methods and status codes:

```
GET    /api/v1/rooms              # List all rooms
GET    /api/v1/rooms/{id}         # Get room details
POST   /api/v1/rooms              # Create new room
PUT    /api/v1/rooms/{id}         # Update room
DELETE /api/v1/rooms/{id}         # Delete room

GET    /api/v1/meetings           # List all meetings
GET    /api/v1/meetings/{id}      # Get meeting details
POST   /api/v1/meetings           # Create meeting
PUT    /api/v1/meetings/{id}      # Update meeting
DELETE /api/v1/meetings/{id}      # Cancel meeting

GET    /api/v1/rooms/{id}/status  # Get current room status
```

### Response Format

**Success Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Conference Room A",
    "capacity": 10
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Room not found",
  "code": "ROOM_NOT_FOUND"
}
```

### WebSocket Events (Real-time Updates)

```javascript
// Server -> Client
{
  "event": "room_status_changed",
  "data": {
    "room_id": 1,
    "status": "occupied",
    "current_meeting": {...}
  }
}

// Client -> Server
{
  "action": "subscribe_room",
  "room_id": 1
}
```

---

## Deployment Considerations

### Raspberry Pi Requirements

**Minimum Hardware:**
- Raspberry Pi 3B+ or newer
- 8GB microSD card (16GB+ recommended)
- 5V 2.5A power supply
- Display (HDMI)
- Network connection (WiFi or Ethernet)

**Optional Hardware:**
- LED status indicators
- Touch screen display
- PIR motion sensor
- NFC/RFID reader for check-in

### Docker Deployment

**Build for ARM:**
```bash
# Build for ARM64
docker buildx build --platform linux/arm64 -t raspberrymeet:latest .

# Build for ARM32v7 (older Raspberry Pi)
docker buildx build --platform linux/arm/v7 -t raspberrymeet:latest .
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/meetings.db
    volumes:
      - ./data:/app/data
    devices:
      - /dev/gpiomem:/dev/gpiomem  # GPIO access

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### Systemd Service (Production)

Create `/etc/systemd/system/raspberrymeet.service`:
```ini
[Unit]
Description=RaspberryMeet Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/RaspberryMeet
ExecStart=/home/pi/RaspberryMeet/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable raspberrymeet
sudo systemctl start raspberrymeet
```

---

## Security Considerations

### API Security
- Use API keys or JWT tokens for authentication
- Implement rate limiting
- Validate all input data
- Use HTTPS in production
- Never expose internal error details to clients

### Environment Variables
Never commit sensitive data. Use `.env` files:
```
# .env.example
BBB_SERVER_URL=https://bbb.example.eu/bigbluebutton/
BBB_API_SECRET=your-bbb-api-secret-here
BBB_DEFAULT_ROOM_URL=https://bbb.example.eu/b/room-abc-def
BBB_DEFAULT_ROOM_PASSWORD=secure-room-password

CALDAV_URL=https://nextcloud.example.eu/remote.php/dav
CALDAV_USERNAME=meeting-room-1@example.eu
CALDAV_PASSWORD=secure-caldav-password

LOG_LEVEL=INFO
ENVIRONMENT=production
```

### GPIO Security
- Run with minimum required privileges
- Validate pin numbers before use
- Implement hardware watchdog for critical operations

---

## AI Assistant Guidelines

### When Working on This Project

1. **Read Current State First:**
   - Always check the current file structure
   - Review existing code before adding new features
   - Check git status and branch

2. **Follow Established Patterns:**
   - If backend exists, match its structure
   - If testing exists, add tests for new features
   - If linting is configured, run it before committing

3. **Documentation:**
   - Update README.md when adding major features
   - Add docstrings/comments for complex logic
   - Update API.md when changing endpoints
   - Keep CLAUDE.md updated with new conventions

4. **Testing:**
   - Write tests for new features
   - Ensure existing tests pass
   - Mock hardware interactions in tests

5. **Hardware-Specific:**
   - Provide fallback for missing hardware
   - Document GPIO pin usage
   - Consider power consumption
   - Test on Raspberry Pi when possible

6. **Git Operations:**
   - Commit frequently with clear messages
   - Push to correct branch (must start with 'claude/')
   - Use retry logic for network failures (2s, 4s, 8s, 16s backoff)
   - Create pull requests when feature is complete

7. **Error Handling:**
   - Handle hardware failures gracefully
   - Log errors appropriately
   - Provide user-friendly error messages
   - Never crash on hardware disconnect

8. **Performance:**
   - Optimize for Raspberry Pi's limited resources
   - Minimize memory usage
   - Use async operations for I/O
   - Consider battery usage if portable

### Common Tasks

**Adding a New API Endpoint:**
1. Define Pydantic model in `backend/app/models/`
2. Create endpoint in `backend/app/api/`
3. Add business logic to `backend/app/services/`
4. Write tests in `backend/tests/`
5. Update `docs/API.md`

**Adding a New UI Component:**
1. Create component in `frontend/src/components/`
2. Add PropTypes or TypeScript types
3. Create corresponding CSS/styles
4. Write component tests
5. Import and use in parent component

**Adding Hardware Control:**
1. Create driver in `hardware/drivers/`
2. Add mock implementation for testing
3. Document in `hardware/specs/`
4. Add GPIO pin mapping to config
5. Write tests with mocked GPIO

### BigBlueButton-Specific Considerations

**BBB Server Configuration:**
- Request BBB server URL and API secret from server administrator
- Test room access before deployment
- Configure default room with password protection
- Map calendar meetings to BBB room names/URLs

**Browser Automation Challenges:**
- BBB UI may change between versions - keep selectors flexible
- Handle permission prompts (microphone, camera) programmatically
- Implement retry logic for network issues
- Monitor for BBB error messages and handle gracefully

**Audio/Video Device Management:**
- Ensure conference speakerphone is detected before joining
- Fall back to HDMI audio if preferred device unavailable
- Test echo cancellation and noise suppression settings
- Validate camera is functional before meeting join

**GPIO Button Behavior:**
- Short press: Join default meeting
- Long press (3s): Show configuration menu (optional)
- Double-press: Mute/unmute toggle
- LED feedback: Immediate visual confirmation

### Questions to Ask

Before implementing features, consider asking:
- **BBB Server Details:** URL, API secret, available rooms?
- **CalDAV Server:** Nextcloud, Radicale, or other? Self-hosted or provider?
- **GPIO Layout:** How many buttons? Which pins? What LED colors?
- **Conference Device:** USB or Bluetooth? Specific model?
- **Auto-Join Behavior:** On boot, or wait for button/calendar?
- **Language:** German UI, English UI, or both?
- **Network:** Static IP or DHCP? WiFi or Ethernet?
- **Web Interface:** Which port (default 8080)? Authentication method (Basic Auth, JWT)?
- **Web Features Priority:** What should be in MVP vs. later versions?

---

## Troubleshooting

### Common Issues

**GPIO Permission Denied:**
```bash
sudo usermod -a -G gpio $USER
# Or run with sudo (not recommended for production)
```

**Docker ARM Build Issues:**
```bash
# Set up buildx
docker buildx create --use
docker buildx inspect --bootstrap
```

**Display Issues on Raspberry Pi:**
```bash
# Force HDMI output
sudo raspi-config
# Select Display Options -> Resolution
```

**Database Locked (SQLite):**
```python
# Use WAL mode
PRAGMA journal_mode=WAL;
```

---

## Resources and Documentation

### Official Documentation
- **BigBlueButton:** https://docs.bigbluebutton.org/
- **BigBlueButton API:** https://docs.bigbluebutton.org/dev/api.html
- **Raspberry Pi:** https://www.raspberrypi.org/documentation/
- **gpiozero:** https://gpiozero.readthedocs.io/
- **Selenium Python:** https://selenium-python.readthedocs.io/
- **Playwright Python:** https://playwright.dev/python/

### Useful Libraries
- **Browser Automation:**
  - `selenium` - Browser automation (stable, widely used)
  - `playwright` - Modern browser automation (faster, more reliable)
  - `undetected-chromedriver` - Avoid bot detection

- **Calendar Integration:**
  - `caldav` - CalDAV protocol client
  - `icalendar` - iCalendar parsing
  - `vobject` - vCard/iCalendar library

- **Audio/Video:**
  - `pulsectl` - PulseAudio control from Python
  - `pyalsaaudio` - ALSA audio interface
  - `v4l2-python` - Video4Linux2 camera control

- **GPIO Control:**
  - `gpiozero` - High-level GPIO interface (recommended)
  - `RPi.GPIO` - Low-level GPIO library
  - `pigpio` - Advanced GPIO with PWM support

- **Scheduling:**
  - `APScheduler` - Advanced Python scheduler
  - `schedule` - Simple job scheduling

### CalDAV Servers (Privacy-Friendly)
- **Nextcloud:** https://nextcloud.com/ (full groupware, EU-hostable)
- **Radicale:** https://radicale.org/ (minimal, Python-based)
- **Baikal:** https://sabre.io/baikal/ (lightweight PHP)
- **SOGo:** https://sogo.nu/ (enterprise groupware)

### Learning Resources
- Raspberry Pi GPIO basics: https://www.raspberrypi-spy.co.uk/
- BigBlueButton development: https://docs.bigbluebutton.org/dev/guide.html
- CalDAV protocol: https://datatracker.ietf.org/doc/html/rfc4791
- Selenium best practices: https://www.selenium.dev/documentation/test_practices/
- Kiosk mode setup: https://pimylifeup.com/raspberry-pi-kiosk/

### Reference Projects
- **pimeet:** https://github.com/pmansour/pimeet (Google Meet automation on Pi)
- **BigBlueButton HTML5 Client:** https://github.com/bigbluebutton/bigbluebutton-html5

---

## Changelog

### 2025-11-15 - BigBlueButton Specification
- Updated CLAUDE.md with BigBlueButton-specific requirements
- Defined kiosk + orchestrator architecture pattern
- Specified CalDAV integration for privacy compliance
- Documented GPIO button interface design
- Added hardware specifications (Pi 4, conference phone, webcam)
- Established EU-only/open-source technology constraints
- Created detailed project structure for BBB client
- Documented browser automation approaches

### 2025-11-15 - Initial Setup
- Created CLAUDE.md with comprehensive project guidelines
- Established project structure recommendations
- Defined coding standards and conventions
- Set up git workflow and branch strategy

---

## Contact and Support

**Project Maintainer:** Sico93 (sico93@posteo.de)

**Contributing:**
- Read CONTRIBUTING.md (to be created)
- Fork the repository
- Create feature branch
- Submit pull request

---

*This document should be updated whenever significant architectural decisions are made or new conventions are established.*
