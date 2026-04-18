"""
TCP message framing: 4-byte big-endian length header + UTF-8 JSON body.

All communication between client and server uses this module so both sides
speak the same wire format regardless of how much data arrives per recv().
"""
import json
import struct
import socket
from typing import Optional

HEADER_SIZE = 4
MAX_MESSAGE_BYTES = 10 * 1024 * 1024  # 10 MB hard limit per message


def encode(msg_type: str, payload: dict) -> bytes:
    """Serialize a message to length-prefixed bytes ready for sendall()."""
    body = json.dumps({"type": msg_type, "payload": payload}).encode("utf-8")
    return struct.pack(">I", len(body)) + body


def recv(sock: socket.socket) -> Optional[dict]:
    """
    Read exactly one message from *sock*.
    Returns the parsed dict, or None if the connection was closed or timed out.
    Raises ValueError if the declared message length exceeds MAX_MESSAGE_BYTES.
    """
    header = _recv_exact(sock, HEADER_SIZE)
    if header is None:
        return None
    length = struct.unpack(">I", header)[0]
    if length > MAX_MESSAGE_BYTES:
        raise ValueError(f"Oversized message: {length} bytes declared")
    body = _recv_exact(sock, length)
    if body is None:
        return None
    return json.loads(body.decode("utf-8"))


def _recv_exact(sock: socket.socket, n: int) -> Optional[bytes]:
    """Accumulate exactly *n* bytes, handling partial recv() calls."""
    buf = bytearray()
    while len(buf) < n:
        try:
            chunk = sock.recv(n - len(buf))
        except OSError:
            # Covers socket.timeout (subclass of OSError since Py 3.3),
            # ConnectionResetError, and any other socket-level failure.
            return None
        if not chunk:
            return None
        buf.extend(chunk)
    return bytes(buf)