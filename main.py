#!/usr/bin/env python3
"""
Main entry point për Klientin - Grupi 33
Rrjetat Kompjuterike 2025/26
"""

import sys
import os

# Shto folderin 'client' në path që Python të gjejë module-t
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'client'))

from client.config import SERVER_HOST, SERVER_PORT, CONNECTION_TIMEOUT
from client.commands import CommandHandler

import socket
import json
class TCPClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.is_admin = False
        self.command_handler = CommandHandler(self)
    def connect(self):
        """Lidhu me serverin"""
        try:
            print(f"[+] Duke u lidhur me {SERVER_HOST}:{SERVER_PORT}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(CONNECTION_TIMEOUT)
            self.socket.connect((SERVER_HOST, SERVER_PORT))
            self.connected = True

            response = self.receive()
            if response:
                print(f"\n[SERVER]: {response.get('message', '')}")
                print(f"Privilegjet: {response.get('permissions', 'unknown')}")
                self.is_admin = "write" in response.get('permissions', '')

            return True

        except Exception as e:
            print(f"[!] Gabim në lidhje: {e}")
            return False    
    def receive(self):
        """Merr përgjigje nga serveri"""
        try:
            data = self.socket.recv(4096).decode('utf-8')
            if not data:
                return None
            return json.loads(data)
        except json.JSONDecodeError:
            return {"raw": data}
        except Exception as e:
            print(f"[!] Gabim në marrje: {e}")
            return None

    def send(self, message):
        """Dërgo mesazh tek serveri"""
        try:
            self.socket.send(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"[!] Gabim në dërgim: {e}")
            self.connected = False
            return False    
    def display_response(self, response):
        """Shfaq përgjigjen nga serveri"""
        status = response.get('status', 'unknown')

        if status == 'error':
            print(f"[GABIM]: {response.get('message', 'Gabim i panjohur')}")

        elif status == 'success':
            if 'files' in response:
                files = response['files']
                if files:
                    print(f"\nFile-t ({len(files)}):")
                    for f in files:
                        print(f"  - {f}")
                else:
                    print("Nuk ka file.")

            elif 'content' in response:
                print(f"\n--- PËRMBAJTJA ---\n{response['content']}\n--- FUND ---")

            elif 'info' in response:
                info = response['info']
                print(f"\nInfo për '{info['filename']}':")
                print(f"  Madhësia: {info['size_kb']} KB ({info['size_bytes']} bytes)")
                print(f"  Krijuar: {info['created']}")
                print(f"  Modifikuar: {info['modified']}")

            else:
                print(f"[OK]: {response.get('message', 'Sukses')}")

        else:
            if 'message' in response:
                print(f"[INFO]: {response['message']}")    