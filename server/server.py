import socket
import threading
import signal
import sys

from config import SERVER_HOST, SERVER_PORT, MAX_CLIENTS, GROUP_IPS, ADMIN_IP
from client_handler import ClientHandler
from http_server import start_http_server


class TCPServer:
    def __init__(self):
        self.server_socket = None
        self.running = False
        self.clients = {}

        self.stats = {
            "active_connections": 0,
            "total_messages": 0,
            "client_ips": set(),
            "messages_log": []
        }

        # HTTP server
        self.http_server = start_http_server(self.stats)

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((SERVER_HOST, SERVER_PORT))
            self.server_socket.listen(MAX_CLIENTS)
            self.running = True

            print("=" * 50)
            print("SERVERI TCP - Grupi 33")
            print("=" * 50)
            print(f"Socket server: {SERVER_HOST}:{SERVER_PORT}")
            print(f"HTTP server:   http://{SERVER_HOST}:8080/stats")
            print(f"Max klientë:   {MAX_CLIENTS}")
            print(f"Grupi IP-të:   {', '.join(GROUP_IPS)}")
            print(f"Admin IP:      {ADMIN_IP}")
            print("=" * 50)
            print("Pres për lidhje...")

            signal.signal(signal.SIGINT, self.shutdown)

            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_socket, client_address = self.server_socket.accept()

                    if len(self.clients) >= MAX_CLIENTS:
                        print(f"[!] Refuzuar {client_address} - limiti i arritur")
                        client_socket.send(b'{"error": "Server i zene"}')
                        client_socket.close()
                        continue

                    handler = ClientHandler(
                        client_socket,
                        client_address,
                        self.stats,
                        self.on_client_disconnect
                    )

                    self.clients[client_address] = handler
                    handler.start()

                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[!] Gabim: {e}")

        except Exception as e:
            print(f"[!] Gabim fatal: {e}")
        finally:
            self.shutdown()

    def on_client_disconnect(self, address):
        self.clients.pop(address, None)

    def shutdown(self, signum=None, frame=None):
        print("\n[!] Mbyllja e serverit...")
        self.running = False

        for handler in list(self.clients.values()):
            handler.running = False
            try:
                handler.client_socket.close()
            except:
                pass

        if self.server_socket:
            self.server_socket.close()

        print("[OK] Serveri u mbyll.")
        sys.exit(0)


if __name__ == "__main__":
    server = TCPServer()
    server.start()