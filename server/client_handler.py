"""
Per-client thread.

Lifecycle:
  1. Set socket timeout (inactivity guard).
  2. Authenticate: first message must be {"type":"auth","payload":{"token":"..."}}.
  3. Register with ConnectionManager (may reject if server is full).
  4. Message loop: dispatch "message" or "command" frames until disconnect.
  5. Cleanup: remove session, close socket.

Priority model:
  Admin clients run in fully independent daemon threads with no artificial
  throttle.  Regular (read-only) clients share the same thread-per-connection
  model but cannot issue file commands -- the asymmetry appears at the
  protocol level rather than the OS scheduler level, which is both portable
  and auditable.
"""
import socket
import threading

from server.config import ADMIN_TOKEN, CLIENT_TIMEOUT_SECONDS
from server import file_manager
from shared import protocol


class ClientHandler(threading.Thread):
    """One thread per connected client."""

    def __init__(
        self,
        sock: socket.socket,
        address: tuple,
        conn_manager,
        message_log,
    ) -> None:
        addr_str = f"{address[0]}:{address[1]}"
        super().__init__(name=f"Client-{addr_str}", daemon=True)
        self._sock         = sock
        self._address      = address
        self._addr_str     = addr_str
        self._conn_manager = conn_manager
        self._msg_log      = message_log
        self._is_admin     = False

    # -- Thread entry ----------------------------------------------------------

    def run(self) -> None:
        # Socket-level timeout is the primary inactivity mechanism.
        # OSError (including socket.timeout) propagates as None from protocol.recv().
        self._sock.settimeout(CLIENT_TIMEOUT_SECONDS)
        try:
            if self._authenticate():
                self._message_loop()
        except OSError:
            pass
        finally:
            self._conn_manager.remove(self._addr_str)
            try:
                self._sock.close()
            except OSError:
                pass
            print(f"[DISCONNECT] {self._addr_str}")

    # -- Authentication --------------------------------------------------------

    def _authenticate(self) -> bool:
        msg = protocol.recv(self._sock)
        if not msg or msg.get("type") != "auth":
            self._send("error", {"message": "First frame must be an auth request"})
            return False

        token          = msg.get("payload", {}).get("token", "")
        self._is_admin = (token == ADMIN_TOKEN)

        if not self._conn_manager.try_accept(self._sock, self._address, self._is_admin):
            return False  # rejection message already sent by ConnectionManager

        role = "admin" if self._is_admin else "readonly"
        self._send("auth_ok", {"role": role})
        self._msg_log.add(self._addr_str, role, f"<connected as {role}>")
        print(f"[CONNECT] {self._addr_str} -> {role}")
        return True