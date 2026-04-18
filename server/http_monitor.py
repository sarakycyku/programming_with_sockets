"""
HTTP monitoring server -- runs in its own daemon thread.

Endpoints:
  GET /stats   ->  200 application/json  (server statistics)
  GET /         ->  302 redirect to /stats (convenience)
  *             ->  404
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from server.config import HTTP_PORT


class _StatsHandler(BaseHTTPRequestHandler):
    """Stateless HTTP handler; connection_manager injected as a class attribute."""

    connection_manager = None  # set by HTTPMonitor.__init__

    # -- Request handling ------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", ""):
            self._redirect("/stats")
        elif self.path == "/stats":
            self._serve_stats()
        else:
            self._not_found()

    # -- Helpers ---------------------------------------------------------------

    def _serve_stats(self) -> None:
        stats = self.connection_manager.get_stats()
        body  = json.dumps(stats, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type",   "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control",  "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str) -> None:
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def _not_found(self) -> None:
        body = b"Not Found\n"
        self.send_response(404)
        self.send_header("Content-Type",   "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        # Suppress the default per-request access log to keep the console clean.
        pass


class HTTPMonitor:
    """Wraps the HTTP server and manages its background thread."""

    def __init__(self, connection_manager) -> None:
        _StatsHandler.connection_manager = connection_manager
        self._server = HTTPServer(("0.0.0.0", HTTP_PORT), _StatsHandler)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            daemon=True,
            name="HTTPMonitor",
        )

    def start(self) -> None:
        self._thread.start()
        print(f"[HTTP]  Stats endpoint -> http://0.0.0.0:{HTTP_PORT}/stats")

    def stop(self) -> None:
        self._server.shutdown()
