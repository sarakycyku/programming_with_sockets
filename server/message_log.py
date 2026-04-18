"""
Thread-safe message store.

Keeps the last MAX_STORED_MESSAGES entries in a deque (for /stats) and
simultaneously writes every entry to a rotating log file via the stdlib
logging module.
"""
import logging
import threading
import time
from collections import deque
from typing import List

from server.config import LOG_FILE, MAX_STORED_MESSAGES

# -- File + console logging setup ----------------------------------------------
_fmt = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format=_fmt)
_console = logging.StreamHandler()
_console.setFormatter(logging.Formatter(_fmt))
logging.getLogger().addHandler(_console)

logger = logging.getLogger(__name__)


class MessageLog:
    """Append-only, thread-safe log of client messages."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._entries: deque = deque(maxlen=MAX_STORED_MESSAGES)

    def add(self, sender_addr: str, role: str, text: str) -> None:
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "sender":    sender_addr,
            "role":      role,
            "text":      text,
        }
        with self._lock:
            self._entries.append(entry)
        logger.info("[%s/%s] %s", role, sender_addr, text)

    def get_all(self) -> List[dict]:
        with self._lock:
            return list(self._entries)

    def get_count(self) -> int:
        with self._lock:
            return len(self._entries)
