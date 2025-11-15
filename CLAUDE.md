# CLAUDE.md - AI Assistant Guide for RaspberryMeet

**Last Updated:** 2025-11-15
**Repository:** RaspberryMeet
**Author:** Sico93 (sico93@posteo.de)

---

## Project Overview

**RaspberryMeet** is a Raspberry Pi-based meeting board application designed to provide a cost-effective alternative to professional meeting room displays. The system will manage meeting room availability, scheduling, and status display.

**Project Description (DE):**
*Ein Meeting Computer, der eine günstige Nachstellung von professionellen Meetingboards abbilden soll.*

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
- Backend server for meeting management
- Frontend UI for display and control
- Hardware interface layer for Raspberry Pi GPIO/display
- Database for meeting data
- Calendar integration (Google Calendar, Outlook, etc.)
- Configuration management
- Testing infrastructure
- Deployment system

---

## Recommended Technology Stack

### Backend Options (Choose One)
1. **Python + FastAPI** (Recommended)
   - Excellent Raspberry Pi support
   - Modern async capabilities
   - Great GPIO libraries (RPi.GPIO, gpiozero)
   - Easy API development
   - Dependencies: `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`

2. **Node.js + Express**
   - Lightweight and fast
   - Good real-time support with Socket.IO
   - ARM compatibility
   - Dependencies: `express`, `socket.io`, `sqlite3`

3. **Go**
   - Excellent performance on ARM
   - Single binary deployment
   - Low memory footprint
   - Ideal for embedded systems

### Frontend Options (Choose One)
1. **React** (Recommended)
   - Modern, component-based
   - Excellent ecosystem
   - Real-time updates with WebSocket
   - Dependencies: `react`, `react-router`, `axios`

2. **Vue.js**
   - Lightweight alternative
   - Easier learning curve
   - Good for small teams

3. **Vanilla HTML/CSS/JS**
   - Minimal overhead
   - Best for simple displays
   - No build process needed

### Database
- **SQLite** (Recommended for single device)
  - No server required
  - Perfect for Raspberry Pi
  - Easy backup and migration

- **PostgreSQL** (For multi-device deployments)

### Hardware Integration (Python)
- **RPi.GPIO** - Standard GPIO control
- **gpiozero** - High-level GPIO interface
- **adafruit-circuitpython** - Advanced sensors/displays

### Container & Deployment
- **Docker** (ARM32v7/ARM64v8 compatible images)
- **docker-compose** for local development
- **systemd** for service management on Raspberry Pi

---

## Recommended Project Structure

```
RaspberryMeet/
├── .github/
│   └── workflows/
│       ├── test.yml           # CI testing pipeline
│       └── build.yml          # Build ARM images
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # Application entry point
│   │   ├── api/               # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── meetings.py
│   │   │   └── rooms.py
│   │   ├── models/            # Database models
│   │   │   ├── __init__.py
│   │   │   ├── meeting.py
│   │   │   └── room.py
│   │   ├── services/          # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── calendar.py
│   │   │   └── hardware.py
│   │   └── config/            # Configuration
│   │       ├── __init__.py
│   │       └── settings.py
│   ├── tests/
│   │   ├── test_api.py
│   │   └── test_services.py
│   ├── requirements.txt       # Python dependencies
│   ├── requirements-dev.txt   # Development dependencies
│   └── pytest.ini             # Test configuration
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── MeetingCard.jsx
│   │   │   └── RoomStatus.jsx
│   │   ├── services/          # API clients
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── index.jsx
│   ├── package.json
│   └── vite.config.js         # Build configuration
├── hardware/
│   ├── drivers/               # GPIO and display drivers
│   │   ├── led_controller.py
│   │   └── display_manager.py
│   ├── specs/                 # Hardware specifications
│   │   ├── HARDWARE.md
│   │   └── wiring.md
│   └── config/                # Hardware configuration
│       └── gpio_mapping.json
├── docs/
│   ├── ARCHITECTURE.md        # System design
│   ├── SETUP.md               # Installation guide
│   ├── API.md                 # API documentation
│   ├── HARDWARE.md            # Hardware setup guide
│   └── DEPLOYMENT.md          # Deployment instructions
├── scripts/
│   ├── setup.sh               # Initial setup
│   ├── run_dev.sh             # Development server
│   ├── deploy.sh              # Deploy to Raspberry Pi
│   └── test.sh                # Run all tests
├── docker/
│   ├── Dockerfile             # Production image
│   ├── Dockerfile.dev         # Development image
│   └── docker-compose.yml     # Local development
├── .gitignore                 # Git ignore patterns
├── .editorconfig              # Editor configuration
├── .env.example               # Environment variables template
├── LICENSE                    # Open source license
├── README.md                  # Project overview
├── CLAUDE.md                  # This file
└── CONTRIBUTING.md            # Contribution guidelines
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
DATABASE_URL=sqlite:///./data/meetings.db
API_KEY=your-api-key-here
CALENDAR_CLIENT_ID=your-google-client-id
CALENDAR_CLIENT_SECRET=your-google-client-secret
SECRET_KEY=your-secret-key-for-jwt
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

### Questions to Ask

Before implementing features, consider asking:
- What hardware will be used? (Display size, GPIO pins needed)
- Which calendar service to integrate? (Google, Outlook, CalDAV)
- Authentication requirements? (None, basic auth, OAuth)
- Deployment target? (Single Pi, multiple devices, cloud-connected)
- Language preference? (German, English, both)
- Display mode? (Kiosk mode, windowed, web-only)

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
- **Raspberry Pi:** https://www.raspberrypi.org/documentation/
- **FastAPI:** https://fastapi.tiangolo.com/
- **React:** https://react.dev/
- **RPi.GPIO:** https://sourceforge.net/p/raspberry-gpio-python/wiki/Home/

### Useful Libraries
- **Calendar Integration:**
  - Google Calendar API: `google-api-python-client`
  - Microsoft Graph: `msal` + `requests`

- **Display/Graphics:**
  - `pygame` - For custom displays
  - `pillow` - Image processing

- **Database:**
  - `sqlalchemy` - ORM
  - `alembic` - Database migrations

### Learning Resources
- Raspberry Pi GPIO basics: https://www.raspberrypi-spy.co.uk/
- FastAPI tutorial: https://fastapi.tiangolo.com/tutorial/
- React hooks: https://react.dev/reference/react

---

## Changelog

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
