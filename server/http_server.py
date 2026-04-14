

from http.server import HTTPServer, BaseHTTPRequestHandler


class StatsHandler(BaseHTTPRequestHandler):
    server_stats = None

    def log_message(self, format, *args):
        # Mos log-o në console (të heshtur)
        pass
