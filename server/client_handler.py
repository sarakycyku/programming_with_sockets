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
        
    def run(self):
        """Trajtimi i lidhjes me klientin"""
        print(f"Klient i ri: {self.client_address} (Admin: {self.is_admin})")
        
        welcome_msg = {
            "type": "welcome",
            "message": f"Mireserdhe! Ti je {'ADMIN' if self.is_admin else 'klient'}",
            "ip": self.client_ip,
            "permissions": "read,write,execute" if self.is_admin else "read"
        }
        self.send_message(welcome_msg)
        
        self.server_stats["active_connections"] += 1
        self.server_stats["total_messages"] += 1
        self.server_stats["client_ips"].add(self.client_ip)
        self.server_stats["messages_log"].append({
            "time": time.strftime("%H:%M:%S"),
            "ip": self.client_ip,
            "type": "connect",
            "message": "Klient u lidh"
        })
        
        try:
            self.client_socket.settimeout(5.0) 
            
            while self.running:
                if time.time() - self.last_activity > CLIENT_TIMEOUT:
                    print(f"Timeout per {self.client_address}")
                    timeout_msg = {"type": "error", "message": "Lidhja u mbyll sepse nuk ka aktivitet"}
                    self.send_message(timeout_msg)
                    break
                
                try:
                    data = self.client_socket.recv(4096).decode('utf-8')
                    if not data:
                        break
                    
                    self.last_activity = time.time()  
                    self.handle_message(data)
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error: {e}")
                    break
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.disconnect()