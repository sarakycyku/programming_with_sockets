import socket
import threading
import json
import time
from config import CLIENT_TIMEOUT, ADMIN_IP
from file_manager import FileManager

class ClientHandler(threading.Thread):
    def __init__(self, client_socket, client_address, server_stats, on_disconnect):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.client_ip = client_address[0]
        self.server_stats = server_stats
        self.on_disconnect = on_disconnect
        self.file_manager = FileManager()
        self.is_admin = (self.client_ip == ADMIN_IP)
        self.running = True
        self.last_activity = time.time()
        
   