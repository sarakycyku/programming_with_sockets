import socket
import os

HOST = input("Shkruani IP e serverit (p.sh. 127.0.0.1): ")
PORT = 12345

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

print(s.recv(1024).decode())

while True:
    cmd = input("\nadmin> ").strip()
    
    if cmd == '/quit':
        break
    
    s.send(cmd.encode())
    
    if cmd.startswith('/upload '):
        fname = cmd[8:]
        if os.path.exists(fname):
            print(s.recv(1024).decode())
            with open(fname, 'rb') as f:
                s.send(f.read())
            print(s.recv(1024).decode())
        else:
            print(f"File '{fname}' nuk u gjet")
    
    elif cmd.startswith('/download '):
        fname = cmd[10:]
        data = s.recv(1024*1024)
        if data.startswith(b'File nuk'):
            print(data.decode())
        else:
            with open(f"downloaded_{fname}", 'wb') as f:
                f.write(data)
            print(f"File '{fname}' u shkarkua")
    
    else:
        print(s.recv(4096).decode())

s.close()