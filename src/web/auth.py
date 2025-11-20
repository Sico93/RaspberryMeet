"""
Authentication and authorization for the web interface.
"""
import hashlib
import secrets
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.utils.config import WebConfig
from src.utils.logger import setup_logger


logger = setup_logger(__name__)
security = HTTPBasic()


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.

    Args:
        password: Plain text password

    Returns:
        SHA-256 hash as hex string with 'sha256:' prefix
    """
    return "sha256:" + hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    Verify a password against a stored password (hash or plain text).

    Supports both SHA-256 hashes (prefixed with 'sha256:') and plain text
    for backwards compatibility.

    Args:
        plain_password: Password provided by user
        stored_password: Stored password (hash or plain text)

    Returns:
        True if password matches, False otherwise
    """
    # Check if stored password is a hash
    if stored_password.startswith("sha256:"):
        # Compare hashes using constant-time comparison
        stored_hash = stored_password[7:]  # Remove 'sha256:' prefix
        computed_hash = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
        return secrets.compare_digest(computed_hash, stored_hash)
    else:
        # Backwards compatibility: plain text comparison
        logger.warning(
            "Using plain text password comparison. "
            "Consider using hashed passwords for better security."
        )
        return secrets.compare_digest(
            plain_password.encode("utf-8"),
            stored_password.encode("utf-8"),
        )


def verify_credentials(
    credentials: HTTPBasicCredentials = Depends(security),
    config: Optional[WebConfig] = None,
) -> str:
    """
    Verify HTTP Basic Auth credentials.

    Supports both SHA-256 hashed passwords and plain text passwords.

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

    # Verify username using constant-time comparison
    correct_username = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        config.username.encode("utf-8"),
    )

    # Verify password (supports both hashed and plain text)
    correct_password = verify_password(credentials.password, config.password)

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
