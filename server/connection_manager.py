"""
Tracks every live client session and enforces capacity limits.

Design decisions:
  - Admin clients bypass MAX_REGULAR_CONNECTIONS so a full regular-client
    pool never locks out the privileged operator.
  - A daemon thread sweeps for timed-out sessions every TIMEOUT_CHECK_INTERVAL
    seconds as a safety net (socket-level timeouts are the primary mechanism).
  - All public methods acquire an RLock so they can be called from any thread.
"""
import socket
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from server.config import (
    CLIENT_TIMEOUT_SECONDS,
    MAX_CONNECTIONS,
    MAX_REGULAR_CONNECTIONS,
    TIMEOUT_CHECK_INTERVAL,
)
from shared import protocol


@dataclass
class ClientSession:
    sock:          socket.socket
    address:       tuple
    is_admin:      bool
    connected_at:  float = field(default_factory=time.time)
    last_active:   float = field(default_factory=time.time)
    message_count: int   = 0

    @property
    def addr_str(self) -> str:
        return f"{self.address[0]}:{self.address[1]}"

    def touch(self) -> None:
        self.last_active = time.time()


class ConnectionManager:
    def __init__(self, message_log) -> None:
        self._sessions: Dict[str, ClientSession] = {}
        self._lock      = threading.RLock()
        self._msg_log   = message_log
        threading.Thread(
            target=self._timeout_monitor,
            daemon=True,
            name="TimeoutMonitor",
        ).start()

    # -- Connection lifecycle ---------------------------------------------------

    def try_accept(
        self,
        sock: socket.socket,
        address: tuple,
        is_admin: bool,
    ) -> bool:
        """
        Register the connection if capacity allows; otherwise send a reject
        message, close the socket, and return False.
        """
        with self._lock:
            total         = len(self._sessions)
            regular_count = sum(1 for s in self._sessions.values() if not s.is_admin)

            if total >= MAX_CONNECTIONS:
                self._reject(sock, "Server is at maximum capacity -- try again later")
                return False
            if not is_admin and regular_count >= MAX_REGULAR_CONNECTIONS:
                self._reject(sock, "No regular-client slots available -- try again later")
                return False

            session = ClientSession(sock=sock, address=address, is_admin=is_admin)
            self._sessions[session.addr_str] = session
            return True

    def remove(self, addr_str: str) -> None:
        with self._lock:
            self._sessions.pop(addr_str, None)

    def get(self, addr_str: str) -> Optional[ClientSession]:
        with self._lock:
            return self._sessions.get(addr_str)

    def touch(self, addr_str: str) -> None:
        with self._lock:
            s = self._sessions.get(addr_str)
            if s:
                s.touch()

    def increment_messages(self, addr_str: str) -> None:
        with self._lock:
            s = self._sessions.get(addr_str)
            if s:
                s.message_count += 1

    # -- Stats ------------------------------------------------------------------

    def get_stats(self) -> dict:
        with self._lock:
            clients: List[dict] = [
                {
                    "ip":              s.address[0],
                    "port":            s.address[1],
                    "role":            "admin" if s.is_admin else "readonly",
                    "messages":        s.message_count,
                    "connected_since": time.strftime(
                        "%Y-%m-%dT%H:%M:%S", time.localtime(s.connected_at)
                    ),
                    "last_active":     time.strftime(
                        "%Y-%m-%dT%H:%M:%S", time.localtime(s.last_active)
                    ),
                }
                for s in self._sessions.values()
            ]
        return {
            "active_connections": len(clients),
            "clients":            clients,
            "total_messages":     self._msg_log.get_count(),
            "stored_messages":    self._msg_log.get_all(),
        }

    # -- Internals --------------------------------------------------------------

    @staticmethod
    def _reject(sock: socket.socket, reason: str) -> None:
        try:
            sock.sendall(protocol.encode("reject", {"reason": reason}))
        except OSError:
            pass
        finally:
            try:
                sock.close()
            except OSError:
                pass

    def _timeout_monitor(self) -> None:
        """Daemon sweep -- secondary defence after socket-level timeouts."""
        while True:
            time.sleep(TIMEOUT_CHECK_INTERVAL)
            now = time.time()
            with self._lock:
                timed_out = [
                    addr
                    for addr, s in self._sessions.items()
                    if (now - s.last_active) > CLIENT_TIMEOUT_SECONDS
                ]
            for addr in timed_out:
                session = self.get(addr)
                if session:
                    try:
                        session.sock.sendall(
                            protocol.encode(
                                "error",
                                {"message": "Disconnected: inactivity timeout"},
                            )
                        )
                        session.sock.close()
                    except OSError:
                        pass
                    self.remove(addr)
                    print(f"[TIMEOUT] Evicted idle client {addr}")
