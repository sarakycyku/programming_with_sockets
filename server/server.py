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