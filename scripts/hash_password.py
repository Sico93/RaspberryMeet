#!/usr/bin/env python3
"""
Password hash generator for RaspberryMeet web interface.

This utility generates SHA-256 hashes for passwords to be used in the .env file.

Usage:
    python scripts/hash_password.py

Or directly:
    python scripts/hash_password.py your-password-here
"""
import sys
import hashlib
import getpass
from pathlib import Path


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.

    Args:
        password: Plain text password

    Returns:
        SHA-256 hash as hex string with 'sha256:' prefix
    """
    return "sha256:" + hashlib.sha256(password.encode("utf-8")).hexdigest()


def main():
    """Main function."""
    print("=" * 60)
    print("🔐 RaspberryMeet Password Hash Generator")
    print("=" * 60)
    print()

    # Get password from command line or prompt
    if len(sys.argv) > 1:
        # Password provided as command line argument
        password = sys.argv[1]
        print("⚠️  WARNING: Providing passwords via command line is insecure!")
        print("   The password may be visible in shell history.")
        print()
    else:
        # Prompt for password (more secure)
        print("Enter the password you want to hash:")
        password = getpass.getpass("Password: ")

        # Confirm password
        password_confirm = getpass.getpass("Confirm password: ")

        if password != password_confirm:
            print("\n❌ Error: Passwords do not match!")
            return 1

    # Validate password
    if not password:
        print("\n❌ Error: Password cannot be empty!")
        return 1

    if len(password) < 8:
        print("\n⚠️  WARNING: Password is less than 8 characters.")
        print("   Consider using a longer password for better security.")
        print()

    # Generate hash
    password_hash = hash_password(password)

    # Display result
    print()
    print("✅ Password hashed successfully!")
    print()
    print("-" * 60)
    print("Add this line to your .env file:")
    print("-" * 60)
    print()
    print(f"WEB_PASSWORD={password_hash}")
    print()
    print("-" * 60)
    print()
    print("📝 Notes:")
    print("   - Store this hash in your .env file (NOT the plain password)")
    print("   - The hash starts with 'sha256:' to indicate it's a hash")
    print("   - Keep your .env file secure and never commit it to git")
    print("   - You can still use plain text passwords, but hashed is more secure")
    print()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(1)
