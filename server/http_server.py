

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
from config import HTTP_HOST, HTTP_PORT



class StatsHandler(BaseHTTPRequestHandler):
    server_stats = None

    def log_message(self, format, *args):
        # Mos log-o në console (të heshtur)
        pass

    # Ky funksion trajton kërkesat GET.
    # Nëse endpoint-i është "/stats", kthen statistikat e serverit në format JSON
    # (lidhjet aktive, numrin total të mesazheve, IP-të e klientëve dhe 20 mesazhet e fundit).


    def do_GET(self):
        if self.path == "/stats":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            stats = {
                "active_connections": self.server_stats["active_connections"],
                "total_messages": self.server_stats["total_messages"],
                "client_ips": list(self.server_stats["client_ips"]),
                "recent_messages": self.server_stats["messages_log"][-20:]  # 20 të fundit
            }

            self.wfile.write(json.dumps(stats, indent=2).encode())
        else:

            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

# Për çdo rrugë tjetër, kthen përgjigje 404 "Not Found".

def start_http_server(stats, host=HTTP_HOST, port=HTTP_PORT):
    """Nis HTTP serverin në thread të veçantë"""
    StatsHandler.server_stats = stats

    server = HTTPServer((host, port), StatsHandler)
    print(f"[HTTP] Server në http://{host}:{port}/stats")

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server