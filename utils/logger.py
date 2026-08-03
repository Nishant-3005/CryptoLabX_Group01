"""
utils/logger.py
---------------
Task 5: Maintains a persistent log file in outputs/cryptolabx.log

Every time the user selects a menu option, a timestamped entry is appended.

Log format:
    [YYYY-MM-DD HH:MM:SS]  ACTION: <option chosen>
"""

import os
from datetime import datetime

# Log file lives in outputs/ folder (created if it doesn't exist)
LOG_DIR  = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
LOG_FILE = os.path.join(LOG_DIR, "cryptolabx.log")


def _ensure_log_dir() -> None:
    """Create the outputs/ directory if it doesn't already exist."""
    os.makedirs(LOG_DIR, exist_ok=True)


def log_action(action: str, detail: str = "") -> None:
    """
    Append a single line to the log file.

    Args:
        action: The menu option selected (e.g. "ENCRYPT", "ANALYZE").
        detail: Optional extra context (e.g. the filename analyzed).
    """
    _ensure_log_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}]  ACTION: {action}"
    if detail:
        entry += f"  |  DETAIL: {detail}"
    entry += "\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)


def log_session_start() -> None:
    """Write a session separator when the program starts."""
    _ensure_log_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separator = f"\n{'='*60}\n  SESSION STARTED  [{timestamp}]\n{'='*60}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(separator)


def show_log() -> None:
    """Print the last 20 lines of the log file to the terminal."""
    if not os.path.exists(LOG_FILE):
        print("  No log file found yet.")
        return
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    recent = lines[-20:] if len(lines) > 20 else lines
    print("\n  \033[93m--- Last Log Entries ---\033[0m")
    for line in recent:
        print("  " + line, end="")
    print()
