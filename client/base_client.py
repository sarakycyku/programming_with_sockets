"""
BaseClient -- socket lifecycle, authentication, send/receive helpers.

Subclasses extend this with role-specific interactive behaviour.
Reconnection is built in: if send_and_recv() loses the connection it
attempts to re-establish up to MAX_RECONNECT_ATTEMPTS times.
"""
import socket
import time
from typing import Optional

from shared import protocol
from client.config import (
    ADMIN_TOKEN,
    CONNECT_TIMEOUT_SECONDS,
    MAX_RECONNECT_ATTEMPTS,
    RECONNECT_DELAY_SECONDS,
    SERVER_HOST,
    SERVER_PORT,
)


class BaseClient:
    def __init__(self, token: str) -> None:
        self._token: str                    = token
        self._sock:  Optional[socket.socket] = None
        self._role:  Optional[str]           = None

    # -- Connection management --------------------------------------------------

    def connect(self, max_attempts: int = MAX_RECONNECT_ATTEMPTS) -> bool:
        """Try to connect and authenticate, retrying up to *max_attempts* times."""
        for attempt in range(1, max_attempts + 1):
            try:
                print(
                    f"[CLIENT] Connecting to {SERVER_HOST}:{SERVER_PORT} "
                    f"(attempt {attempt}/{max_attempts})..."
                )
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(CONNECT_TIMEOUT_SECONDS)
                sock.connect((SERVER_HOST, SERVER_PORT))
                sock.settimeout(None)   # blocking mode after handshake
                self._sock = sock
                if self._authenticate():
                    print(f"[CLIENT] Authenticated -- role: {self._role}")
                    return True
                self._sock = None
                return False
            except (ConnectionRefusedError, OSError, TimeoutError) as exc:
                print(f"[CLIENT] Connection failed: {exc}")
                if attempt < max_attempts:
                    print(f"[CLIENT] Retrying in {RECONNECT_DELAY_SECONDS}s...")
                    time.sleep(RECONNECT_DELAY_SECONDS)
        print("[CLIENT] Could not reach server.")
        return False

    def reconnect(self) -> bool:
        print("[CLIENT] Reconnecting...")
        self.disconnect()
        return self.connect()

    def disconnect(self) -> None:
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
            self._role = None

