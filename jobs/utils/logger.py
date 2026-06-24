"""Standalone logger configuration module."""

import logging
import sys
from datetime import datetime


class CleanFormatter(logging.Formatter):
    """Clean terminal formatter with timestamps and optional ANSI colors."""

    def __init__(self) -> None:
        """Initializes the formatter."""
        super().__init__(datefmt="%Y-%m-%d %H:%M:%S")
        self.use_color = sys.stderr.isatty() and "--no-color" not in sys.argv

    def format(self, record: logging.LogRecord) -> str:
        """Formats log records with custom date format and optional colors."""
        local_tz = datetime.now().astimezone().tzinfo
        asctime = datetime.fromtimestamp(record.created, tz=local_tz).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        if self.use_color:
            cyan, reset = "\x1b[36;20m", "\x1b[0m"
            return f"{cyan}{asctime}{reset} ✨ {record.getMessage()}"
        return f"{asctime} ✨ {record.getMessage()}"


def setup_standalone_logging() -> None:
    """Ensures terminal logs write to stderr to protect stdout streams."""
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(CleanFormatter())
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler]
