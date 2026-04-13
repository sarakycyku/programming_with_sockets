import socket

HOST = input("Shkruani IP e serverit (p.sh. 127.0.0.1): ")
PORT = 12345

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

print(s.recv(1024).decode())

while True:
    cmd = input("\nclient> ").strip()
    
    if cmd == '/quit':
        break
    
    s.send(cmd.encode())
    
    if cmd.startswith('/read ') or cmd == '/list' or cmd.startswith('/search ') or cmd.startswith('/info '):
        print(s.recv(4096).decode())
    else:
        print("Komande e palejuar! Vetem lexim (read)")

s.close()