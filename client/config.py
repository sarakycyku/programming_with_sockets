"""
Client configuration.

Before running clients on a DIFFERENT machine, change SERVER_HOST
to the LAN IP address of the server (e.g. "192.168.1.42").
Find it with: ipconfig (Windows) or ip addr (Linux/macOS).
"""

SERVER_HOST = "172.20.10.7"   # <secili e qitni ip tjuaj per me na bo
SERVER_PORT = 9000

# Must match server/config.py -> ADMIN_TOKEN
ADMIN_TOKEN = "super-secret-admin-token"

CONNECT_TIMEOUT_SECONDS  = 10   # Timeout for the initial TCP connect()
RECONNECT_DELAY_SECONDS  = 3    # Wait between reconnection attempts
MAX_RECONNECT_ATTEMPTS   = 5
