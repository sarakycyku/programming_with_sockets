"""
Central configuration for the TCP server and HTTP monitor.
Edit these values before running -- no other file needs to change.
"""
import os

# -- Network ------------------------------------------------------------------
SERVER_HOST = "0.0.0.0"   # Listen on all network interfaces
SERVER_PORT = 9000         # TCP server port
HTTP_PORT   = 9080         # HTTP monitoring port (GET /stats)

# -- Connection limits ---------------------------------------------------------
MAX_CONNECTIONS         = 4  # Absolute cap on simultaneous clients
MAX_REGULAR_CONNECTIONS = 3   # Cap for non-admin clients (admins bypass this)
CONNECTION_QUEUE_SIZE   = 5   # OS-level listen() backlog

# -- Timeouts ------------------------------------------------------------------
CLIENT_TIMEOUT_SECONDS  = 120  # Seconds of recv inactivity -> disconnect
TIMEOUT_CHECK_INTERVAL  = 15   # How often the background monitor sweeps (seconds)

# -- Authentication ------------------------------------------------------------
ADMIN_TOKEN = "super-secret-admin-token"  # Must match client/config.py

# -- File system ---------------------------------------------------------------
_PROJECT_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_FILES_DIR = os.path.join(_PROJECT_ROOT, "server_files")

# -- Logging -------------------------------------------------------------------
LOG_FILE           = os.path.join(_PROJECT_ROOT, "server.log")
MAX_STORED_MESSAGES = 500  # In-memory deque cap
