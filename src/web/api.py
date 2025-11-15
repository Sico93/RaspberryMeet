"""
FastAPI web application for RaspberryMeet admin interface.
"""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from src.orchestrator.browser_controller import BrowserController
from src.utils.config import load_config
from src.utils.logger import setup_logger
from src.web.auth import get_current_user


logger = setup_logger(__name__)


# Global state
class AppState:
    """Global application state."""
    def __init__(self):
        self.config = load_config()
        self.browser: Optional[BrowserController] = None
        self.meeting_state: MeetingState = MeetingState.IDLE
        self.current_room_url: Optional[str] = None
        self.meeting_start_time: Optional[datetime] = None
        self.websocket_connections: list[WebSocket] = []


state = AppState()


# Enums and Models
class MeetingState(str, Enum):
    """Meeting state enumeration."""
    IDLE = "idle"
    JOINING = "joining"
    ACTIVE = "active"
    LEAVING = "leaving"
    ERROR = "error"


class StatusResponse(BaseModel):
    """System status response."""
    state: MeetingState
    current_room: Optional[str] = None
    meeting_duration: Optional[int] = None  # seconds
    uptime: int
    timestamp: datetime


class JoinRequest(BaseModel):
    """Request to join a meeting."""
    room_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class JoinResponse(BaseModel):
    """Response after joining attempt."""
    success: bool
    message: str
    state: MeetingState


# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting RaspberryMeet Web Interface")
    logger.info(f"Web interface available at http://0.0.0.0:{state.config.web.port}")

    # Startup: Initialize browser controller
    state.browser = BrowserController(
        bbb_config=state.config.bbb,
        headless=state.config.web.headless_browser,
        kiosk_mode=False,  # Kiosk mode controlled via config later
    )

    yield

    # Shutdown: Clean up resources
    logger.info("Shutting down RaspberryMeet Web Interface")
    if state.browser:
        await state.browser.cleanup()


# FastAPI app
app = FastAPI(
    title="RaspberryMeet Admin",
    description="Web admin interface for RaspberryMeet BigBlueButton client",
    version="0.1.0",
    lifespan=lifespan,
)

# Setup templates and static files
templates_dir = Path(__file__).parent / "templates"
static_dir = Path(__file__).parent / "static"

templates_dir.mkdir(exist_ok=True)
static_dir.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(templates_dir))

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# Helper functions
def get_meeting_duration() -> Optional[int]:
    """Get current meeting duration in seconds."""
    if state.meeting_start_time and state.meeting_state == MeetingState.ACTIVE:
        return int((datetime.now() - state.meeting_start_time).total_seconds())
    return None


async def broadcast_status():
    """Broadcast status update to all WebSocket connections."""
    status_data = {
        "state": state.meeting_state.value,
        "current_room": state.current_room_url,
        "duration": get_meeting_duration(),
        "timestamp": datetime.now().isoformat(),
    }

    # Send to all connected clients
    disconnected = []
    for ws in state.websocket_connections:
        try:
            await ws.send_json(status_data)
        except Exception:
            disconnected.append(ws)

    # Remove disconnected clients
    for ws in disconnected:
        state.websocket_connections.remove(ws)


# Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request, username: str = Depends(get_current_user)):
    """Render main dashboard."""
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "username": username,
            "config": state.config,
            "state": state.meeting_state.value,
            "current_room": state.current_room_url,
            "default_room": state.config.bbb.default_room_url,
        }
    )


@app.get("/api/status")
async def get_status(username: str = Depends(get_current_user)) -> StatusResponse:
    """
    Get current system status.

    Returns:
        Current meeting state, room, and timing information
    """
    return StatusResponse(
        state=state.meeting_state,
        current_room=state.current_room_url,
        meeting_duration=get_meeting_duration(),
        uptime=0,  # TODO: Track actual uptime
        timestamp=datetime.now(),
    )


@app.post("/api/meeting/join")
async def join_meeting(
    request: JoinRequest,
    username: str = Depends(get_current_user),
) -> JoinResponse:
    """
    Join a BigBlueButton meeting.

    Args:
        request: Join request with optional room URL, username, password

    Returns:
        Join response with success status
    """
    if state.meeting_state in [MeetingState.JOINING, MeetingState.ACTIVE]:
        return JoinResponse(
            success=False,
            message="Already in a meeting or joining",
            state=state.meeting_state,
        )

    # Update state
    state.meeting_state = MeetingState.JOINING
    state.current_room_url = request.room_url or state.config.bbb.default_room_url
    await broadcast_status()

    try:
        # Ensure browser is started
        if not state.browser._is_running:
            await state.browser.start()

        # Join meeting
        logger.info(f"Joining meeting: {state.current_room_url}")
        success = await state.browser.join_meeting(
            room_url=request.room_url,
            username=request.username,
            password=request.password,
        )

        if success:
            state.meeting_state = MeetingState.ACTIVE
            state.meeting_start_time = datetime.now()
            await broadcast_status()

            return JoinResponse(
                success=True,
                message=f"Successfully joined meeting",
                state=state.meeting_state,
            )
        else:
            state.meeting_state = MeetingState.ERROR
            state.current_room_url = None
            await broadcast_status()

            return JoinResponse(
                success=False,
                message="Failed to join meeting - check logs for details",
                state=state.meeting_state,
            )

    except Exception as e:
        logger.error(f"Error joining meeting: {e}", exc_info=True)
        state.meeting_state = MeetingState.ERROR
        state.current_room_url = None
        await broadcast_status()

        return JoinResponse(
            success=False,
            message=f"Error: {str(e)}",
            state=state.meeting_state,
        )


@app.post("/api/meeting/leave")
async def leave_meeting(username: str = Depends(get_current_user)) -> JoinResponse:
    """
    Leave the current meeting.

    Returns:
        Response with success status
    """
    if state.meeting_state != MeetingState.ACTIVE:
        return JoinResponse(
            success=False,
            message="Not currently in a meeting",
            state=state.meeting_state,
        )

    # Update state
    state.meeting_state = MeetingState.LEAVING
    await broadcast_status()

    try:
        logger.info("Leaving meeting")
        await state.browser.leave_meeting()

        state.meeting_state = MeetingState.IDLE
        state.current_room_url = None
        state.meeting_start_time = None
        await broadcast_status()

        return JoinResponse(
            success=True,
            message="Successfully left meeting",
            state=state.meeting_state,
        )

    except Exception as e:
        logger.error(f"Error leaving meeting: {e}", exc_info=True)
        state.meeting_state = MeetingState.ERROR
        await broadcast_status()

        return JoinResponse(
            success=False,
            message=f"Error: {str(e)}",
            state=state.meeting_state,
        )


@app.post("/api/meeting/join-default")
async def join_default_meeting(username: str = Depends(get_current_user)) -> JoinResponse:
    """
    Join the default meeting room.

    Returns:
        Response with success status
    """
    return await join_meeting(JoinRequest(), username)


@app.get("/api/config/rooms")
async def get_rooms(username: str = Depends(get_current_user)):
    """
    Get configured meeting rooms.

    Returns:
        List of available rooms
    """
    return {
        "default_room": {
            "name": "Default Room",
            "url": state.config.bbb.default_room_url,
            "has_password": bool(state.config.bbb.default_room_password),
        }
    }


@app.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    """
    WebSocket endpoint for real-time status updates.

    Clients connect here to receive live meeting state changes.
    """
    await websocket.accept()
    state.websocket_connections.append(websocket)
    logger.info(f"WebSocket connected. Total connections: {len(state.websocket_connections)}")

    try:
        # Send initial status
        await websocket.send_json({
            "state": state.meeting_state.value,
            "current_room": state.current_room_url,
            "duration": get_meeting_duration(),
            "timestamp": datetime.now().isoformat(),
        })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back for ping/pong
            await websocket.send_text(data)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        state.websocket_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in state.websocket_connections:
            state.websocket_connections.remove(websocket)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": "raspberrymeet-web",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
    }


# Run directly for development
if __name__ == "__main__":
    import uvicorn

    config = load_config()

    uvicorn.run(
        "src.web.api:app",
        host=config.web.host,
        port=config.web.port,
        reload=True,
        log_level="info",
    )
