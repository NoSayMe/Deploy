"""Utility helpers for simple echo behaviour."""

import os


def echo_message(msg: str) -> str:
    """Return the global greeting followed by the provided message."""
    base = os.getenv("GLOBAL_MESSAGE", "Hello from Jenkins FastAPI!")
    return f"{base} - {msg}"
