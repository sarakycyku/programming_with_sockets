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
        