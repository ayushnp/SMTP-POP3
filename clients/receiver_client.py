import socket
import os

HOST="127.0.0.1"
PORT = 1100
client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

print("S: ",client_socket.recv(4096).decode())

print("Connected to POP# server")
print("Type POP3 commands (USER, PASS, LIST, RETR, QUIT)")

while True:
    cmd = input("POP3> ")
    if not cmd:
        continue

    client_socket.send((cmd + "\r\n").encode())

    response = client_socket.recv(4096)
    print("S: "+response.decode())

    if cmd.upper() == "QUIT":
        break

client_socket.close()