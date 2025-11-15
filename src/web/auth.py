"""
Authentication and authorization for the web interface.
"""
import secrets
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.utils.config import WebConfig
from src.utils.logger import setup_logger


logger = setup_logger(__name__)
security = HTTPBasic()


def verify_credentials(
    credentials: HTTPBasicCredentials = Depends(security),
    config: Optional[WebConfig] = None,
) -> str:
    """
    Verify HTTP Basic Auth credentials.

    Args:
        credentials: HTTP Basic credentials
        config: Web configuration (optional, loaded if not provided)

    Returns:
        Username if authenticated

    Raises:
        HTTPException: If credentials are invalid
    """
    if config is None:
        from src.utils.config import load_config
        config = load_config().web

    # Compare credentials using constant-time comparison
    correct_username = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        config.username.encode("utf-8"),
    )
    correct_password = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        config.password.encode("utf-8"),
    )

    if not (correct_username and correct_password):
        logger.warning(f"Failed login attempt for user: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    logger.debug(f"Successful login: {credentials.username}")
    return credentials.username


async def get_current_user(username: str = Depends(verify_credentials)) -> str:
    """
    Dependency to get the current authenticated user.

    Args:
        username: Username from verify_credentials

    Returns:
        Username
    """
    return username
