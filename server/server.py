import socket
import threading
import signal
import sys
from config import SERVER_HOST, SERVER_PORT, MAX_CLIENTS, GROUP_IPS
from client_handler import ClientHandler
from http_server import start_http_server

class TCPServer:
    def __init__(self):
        self.server_socket = None
        self.http_server = None
        self.running = False
        self.clients = {}  # {address: handler}
        
        # Statistikat globale
        self.stats = {
            "active_connections": 0,
            "total_messages": 0,
            "client_ips": set(),
            "messages_log": []
        }
        
        # Nis HTTP server paralel
        self.http_server = start_http_server(self.stats)
    def start(self):
        """Nis serverin kryesor"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((SERVER_HOST, SERVER_PORT))
            self.server_socket.listen(MAX_CLIENTS)
            self.running = True
            
            print(f"=" * 50)
            print(f"SERVERI TCP - Grupi 33")
            print(f"=" * 50)
            print(f"Socket server: {SERVER_HOST}:{SERVER_PORT}")
            print(f"HTTP server:   http://{SERVER_HOST}:8080/stats")
            print(f"Max klientë:   {MAX_CLIENTS}")
            print(f"Grupi IP-të:   {', '.join(GROUP_IPS)}")
            print(f"Admin IP:      {GROUP_IPS[0]}")
            print(f"=" * 50)
            print("Pres për lidhje...")
        # Handle Ctrl+C
            signal.signal(signal.SIGINT, self.shutdown)
            
            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_socket, client_address = self.server_socket.accept()
                    
                    # Kontrollo numrin e klientëve
                    if len(self.clients) >= MAX_CLIENTS:
                        print(f"[!] Refuzuar {client_address} - limiti i arritur")
                        client_socket.send(b'{"error": "Server i zene, provo me vone"}')
                        client_socket.close()
                        continue
                    # Krijo handler për klientin
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
        """Callback kur një klient shkëputet"""
        if address in self.clients:
            del self.clients[address]
    
    def shutdown(self, signum=None, frame=None):
        """Mbylle serverin"""
        print("\n[!] Mbyllja e serverit...")
        self.running = False