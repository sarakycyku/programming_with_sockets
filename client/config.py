# Konfigurimet e serverit - Grupi 33
import os

# IP dhe Porti i serverit kryesor (TCP Socket)
SERVER_HOST = "172.16.107.106"
SERVER_PORT = 5000       # Porti kryesor për TCP socket
CONNECTION_TIMEOUT = 10
# HTTP Server (për statistika)
HTTP_HOST = "0.0.0.0"
HTTP_PORT = 8080

# Pragjet
MAX_CLIENTS = 5          # Maksimumi i klientëve (3 veta + rezervë)
CLIENT_TIMEOUT = 60      # Sekonda për timeout (mbylle lidhjen nëse hesht)

# Folderi për file-t
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "files")

# IP-të e anëtarëve të grupit (3 veta)
GROUP_IPS = ["172.16.107.106", "172.16.107.96", "172.16.107.97"]

# Admin-i (klienti me privilegje të plota) - IP e parë
ADMIN_IP = "172.16.107.106"

# Krijo folderin nëse nuk ekziston
os.makedirs(DATA_DIR, exist_ok=True)