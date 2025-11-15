"""
Configuration management for RaspberryMeet
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


# Load .env file from project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


class BigBlueButtonConfig(BaseModel):
    """BigBlueButton server configuration"""
    server_url: str = Field(..., description="BBB server URL")
    api_secret: Optional[str] = Field(None, description="BBB API secret")
    default_room_url: str = Field(..., description="Default BBB room URL")
    default_room_id: Optional[str] = Field(None, description="Default room ID")
    default_room_password: Optional[str] = Field(None, description="Room password")
    default_username: str = Field(default="RaspberryMeet", description="Default username")


class CalDAVConfig(BaseModel):
    """CalDAV calendar configuration"""
    enabled: bool = Field(default=False, description="Enable CalDAV sync")
    url: Optional[str] = Field(None, description="CalDAV server URL")
    username: Optional[str] = Field(None, description="CalDAV username")
    password: Optional[str] = Field(None, description="CalDAV password")
    calendar_name: str = Field(default="Meetings", description="Calendar name")
    sync_interval_minutes: int = Field(default=5, description="Sync interval")


class WebConfig(BaseModel):
    """Web admin interface configuration"""
    enabled: bool = Field(default=True, description="Enable web interface")
    host: str = Field(default="0.0.0.0", description="Web server host")
    port: int = Field(default=8080, description="Web server port")
    username: str = Field(default="admin", description="Admin username")
    password: str = Field(default="admin", description="Admin password")
    secret_key: str = Field(default="change-me", description="JWT secret key")


class GPIOConfig(BaseModel):
    """GPIO hardware configuration"""
    enabled: bool = Field(default=True, description="Enable GPIO")
    join_button_pin: int = Field(default=17, description="Join button GPIO pin")
    leave_button_pin: int = Field(default=27, description="Leave button GPIO pin")
    mute_button_pin: int = Field(default=22, description="Mute toggle GPIO pin")
    status_led_green_pin: int = Field(default=23, description="Green status LED pin")
    status_led_red_pin: int = Field(default=24, description="Red status LED pin")


class AppConfig(BaseSettings):
    """Main application configuration"""

    # Environment
    environment: str = Field(default="development", description="Environment")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Log level")

    # BigBlueButton
    bbb: BigBlueButtonConfig = Field(default_factory=BigBlueButtonConfig)

    # CalDAV
    caldav: CalDAVConfig = Field(default_factory=CalDAVConfig)

    # Web Interface
    web: WebConfig = Field(default_factory=WebConfig)

    # GPIO
    gpio: GPIOConfig = Field(default_factory=GPIOConfig)

    # Kiosk
    kiosk_mode: bool = Field(default=True, description="Enable kiosk mode")
    auto_join_on_boot: bool = Field(default=False, description="Auto-join on boot")

    class Config:
        env_prefix = ""
        env_nested_delimiter = "_"
        case_sensitive = False


def load_config() -> AppConfig:
    """
    Load configuration from environment variables.

    Returns:
        AppConfig instance
    """
    # Build BBB config from env vars
    bbb_config = BigBlueButtonConfig(
        server_url=os.getenv("BBB_SERVER_URL", ""),
        api_secret=os.getenv("BBB_API_SECRET"),
        default_room_url=os.getenv("BBB_DEFAULT_ROOM_URL", ""),
        default_room_id=os.getenv("BBB_DEFAULT_ROOM_ID"),
        default_room_password=os.getenv("BBB_DEFAULT_ROOM_PASSWORD"),
        default_username=os.getenv("BBB_DEFAULT_USERNAME", "RaspberryMeet"),
    )

    # Build CalDAV config
    caldav_config = CalDAVConfig(
        enabled=os.getenv("CALDAV_ENABLED", "false").lower() == "true",
        url=os.getenv("CALDAV_URL"),
        username=os.getenv("CALDAV_USERNAME"),
        password=os.getenv("CALDAV_PASSWORD"),
        calendar_name=os.getenv("CALDAV_CALENDAR_NAME", "Meetings"),
        sync_interval_minutes=int(os.getenv("CALDAV_SYNC_INTERVAL_MINUTES", "5")),
    )

    # Build Web config
    web_config = WebConfig(
        enabled=os.getenv("WEB_ENABLED", "true").lower() == "true",
        host=os.getenv("WEB_HOST", "0.0.0.0"),
        port=int(os.getenv("WEB_PORT", "8080")),
        username=os.getenv("WEB_USERNAME", "admin"),
        password=os.getenv("WEB_PASSWORD", "admin"),
        secret_key=os.getenv("WEB_SECRET_KEY", "change-me"),
    )

    # Build GPIO config
    gpio_config = GPIOConfig(
        enabled=os.getenv("GPIO_ENABLED", "true").lower() == "true",
        join_button_pin=int(os.getenv("GPIO_JOIN_BUTTON_PIN", "17")),
        leave_button_pin=int(os.getenv("GPIO_LEAVE_BUTTON_PIN", "27")),
        mute_button_pin=int(os.getenv("GPIO_MUTE_BUTTON_PIN", "22")),
        status_led_green_pin=int(os.getenv("GPIO_STATUS_LED_GREEN_PIN", "23")),
        status_led_red_pin=int(os.getenv("GPIO_STATUS_LED_RED_PIN", "24")),
    )

    # Build main config
    config = AppConfig(
        environment=os.getenv("ENVIRONMENT", "development"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        bbb=bbb_config,
        caldav=caldav_config,
        web=web_config,
        gpio=gpio_config,
        kiosk_mode=os.getenv("KIOSK_MODE", "true").lower() == "true",
        auto_join_on_boot=os.getenv("AUTO_JOIN_ON_BOOT", "false").lower() == "true",
    )

    return config


# Global config instance
config = load_config()
