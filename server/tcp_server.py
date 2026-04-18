"""
TCP Server entry point.

Starts:
  1. The HTTP monitoring server (daemon thread).
  2. The TCP server accept loop (main thread).

Each accepted connection gets its own ClientHandler daemon thread.
Ctrl-C / SIGTERM triggers a graceful shutdown.
"""
import os
import signal
import socket
import sys

# Allow running as: python server/tcp_server.py from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.config import CONNECTION_QUEUE_SIZE, SERVER_HOST, SERVER_PORT
from server.connection_manager import ConnectionManager
from server.client_handler import ClientHandler
from server.http_monitor import HTTPMonitor
from server.message_log import MessageLog


def main() -> None:
    message_log  = MessageLog()
    conn_manager = ConnectionManager(message_log)

    http_monitor = HTTPMonitor(conn_manager)
    http_monitor.start()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((SERVER_HOST, SERVER_PORT))
    server_sock.listen(CONNECTION_QUEUE_SIZE)
    print(f"[TCP]   Server listening on {SERVER_HOST}:{SERVER_PORT}")
    print("        Press Ctrl-C to stop.\n")

    def _shutdown(sig, frame) -> None:
        print("\n[SERVER] Shutting down...")
        try:
            server_sock.close()
        except OSError:
            pass
        http_monitor.stop()
        sys.exit(0)

    # Signal handlers can only be installed from the main thread.
    import threading
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGINT, _shutdown)
        if sys.platform != "win32":
            signal.signal(signal.SIGTERM, _shutdown)

    while True:
        try:
            client_sock, address = server_sock.accept()
        except OSError:
            break
        ClientHandler(client_sock, address, conn_manager, message_log).start()


if __name__ == "__main__":
    main()
