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