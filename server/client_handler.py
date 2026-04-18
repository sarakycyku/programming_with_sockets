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

        # Fix: Check both ADMIN_IP and localhost
        self.is_admin = (self.client_ip == ADMIN_IP) or (self.client_ip == "127.0.0.1")

        self.running = True
        self.last_activity = time.time()
        print("CLIENT IP:", self.client_ip)
        print("ADMIN IP:", ADMIN_IP)
        print("IS ADMIN:", self.is_admin)  # Add this debug line
        
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
            
    def handle_message(self, data):
        """Proceso mesazhin e marre"""
        try:
            msg = json.loads(data)
            command = msg.get("command", "")
            args = msg.get("args", [])
            
            print(f" {self.client_address}: {command} {args}")
            
            self.server_stats["total_messages"] += 1
            self.server_stats["messages_log"].append({
                "time": time.strftime("%H:%M:%S"),
                "ip": self.client_ip,
                "type": "command",
                "command": command,
                "args": args
            })
            
            if len(self.server_stats["messages_log"]) > 100:
                self.server_stats["messages_log"] = self.server_stats["messages_log"][-50:]
            
            response = self.process_command(command, args)
            self.send_message(response)
            
        except json.JSONDecodeError:
            self.send_message({"status": "error", "message": "Invalid format JSON"})
        except Exception as e:
            self.send_message({"status": "error", "message": str(e)})
    
    def process_command(self, command, args):
        """Ekzekuto komanden"""
        
        if command == "/list":
            return self.file_manager.list_files()
        
        elif command == "/read":
            if not args:
                return {"status": "error", "message": "Perdor: /read <filename>"}
            return self.file_manager.read_file(args[0])
        
        elif command == "/search":
            if not args:
                return {"status": "error", "message": "Perdor: /search <keyword>"}
            return self.file_manager.search_files(args[0])
        
        elif command == "/info":
            if not args:
                return {"status": "error", "message": "Perdor: /info <filename>"}
            return self.file_manager.file_info(args[0])
        
        elif command in ["/upload", "/delete"]:
            if not self.is_admin:
                return {"status": "error", "message": "Vetem admini mund te ekzekutoje kete komande."}
            
            if command == "/upload":
                if len(args) < 2:
                    return {"status": "error", "message": "Perdor: /upload <filename> <content>"}
                return self.file_manager.upload_file(args[0], args[1])
            
            elif command == "/delete":
                if not args:
                    return {"status": "error", "message": "Perdor: /delete <filename>"}
                return self.file_manager.delete_file(args[0])
        
        elif command == "/download":
            if not args:
                return {"status": "error", "message": "Perdor: /download <filename>"}
            return self.file_manager.download_file(args[0])
        
        elif command == "ping":
            return {"status": "success", "message": "pong", "is_admin": self.is_admin}
        
        else:
            return {"status": "error", "message": f"Komande e panjohur: {command}"}
    
    def send_message(self, message):
        """Dergo mesazh tek klienti"""
        try:
            self.client_socket.send(json.dumps(message).encode('utf-8'))
        except Exception as e:
            print(f" Error ne dergim: {e}")
    
    def disconnect(self):
        """Mbylle lidhjen"""
        if self.running:
            self.running = False
            self.server_stats["active_connections"] -= 1
            self.on_disconnect(self.client_address)
            try:
                self.client_socket.close()
            except:
                pass
            print(f"Klient u shkeput: {self.client_address}")