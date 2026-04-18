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

    # -- Sending helpers ---------------------------------------------------

    def _send(self, msg_type: str, payload: dict) -> bool:
        """Serialize and send a single protocol message. Returns False on error.

        Swallows socket-level OSErrors (including timeouts and resets) so callers
        can treat send failures as a benign disconnect event.
        """
        try:
            self._sock.sendall(protocol.encode(msg_type, payload))
            return True
        except OSError:
            return False

    def _message_loop(self) -> None:
        """Main receive loop: handle 'message' and 'command' frames."""
        while True:
            msg = protocol.recv(self._sock)
            if not msg:
                break

            mtype = msg.get("type", "")
            payload = msg.get("payload", {})

            # Update session activity stats
            try:
                self._conn_manager.touch(self._addr_str)
                self._conn_manager.increment_messages(self._addr_str)
            except Exception:
                pass

            if mtype == "message":
                text = payload.get("text", "")
                role = "admin" if self._is_admin else "readonly"
                self._msg_log.add(self._addr_str, role, text)
                # Acknowledge receipt so clients waiting on recv get a reply
                if not self._send("response", {"message": "ok"}):
                    break

            elif mtype == "command":
                cmd = payload.get("cmd", "")
                args = payload.get("args", []) or []
                resp_payload = self._handle_command(cmd, args)
                if not self._send("response", resp_payload):
                    break

            else:
                # Unknown frame type
                if not self._send("error", {"message": "Unknown frame type"}):
                    break

    def _handle_command(self, cmd: str, args: list) -> dict:
        """Execute admin commands via file_manager and return payload dict."""
        # Commands that operate on server files
        file_cmds = {"/list", "/read", "/upload", "/download", "/delete", "/search", "/info"}

        if cmd in file_cmds and not self._is_admin:
            return {"error": "Permission denied: admin only"}

        try:
            if cmd == "/list":
                return file_manager.list_files()

            if cmd == "/read":
                if not args:
                    return {"error": "Usage: /read <filename>"}
                return file_manager.read_file(args[0])

            if cmd == "/upload":
                if len(args) < 2:
                    return {"error": "Usage: /upload <filename> <content_b64>"}
                return file_manager.write_file(args[0], args[1])

            if cmd == "/download":
                if not args:
                    return {"error": "Usage: /download <filename>"}
                return file_manager.download_file(args[0])

            if cmd == "/delete":
                if not args:
                    return {"error": "Usage: /delete <filename>"}
                return file_manager.delete_file(args[0])

            if cmd == "/search":
                if not args:
                    return {"error": "Usage: /search <keyword>"}
                return file_manager.search_files(args[0])

            if cmd == "/info":
                if not args:
                    return {"error": "Usage: /info <filename>"}
                return file_manager.file_info(args[0])

            return {"error": "Unknown command"}
        except Exception as exc:
            return {"error": str(exc)}