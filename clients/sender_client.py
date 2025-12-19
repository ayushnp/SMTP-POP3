import socket

HOST = "127.0.0.1"
PORT = 2525

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("S:", client.recv(4096).decode())

print("\nConnected to Sender SMTP Server")
print("Commands:")
print("  HELO <domain>")
print("  MAIL FROM:<email>")
print("  RCPT TO:<email>")
print("  DATA")
print("  <message body>")
print("  .   (end DATA)")
print("  QUIT\n")

data_mode = False

while True:
    cmd =input("SMTP> ")

    if data_mode:
        client.send((cmd + "\r\n").encode())
        if cmd=='.':
            print("S: " + client.recv(4096).decode())
            data_mode = False
        continue


    client.send((cmd + "\r\n").encode())
    response = client.recv(4096).decode()
    print("S: "+response)

    if cmd.upper() == "DATA":
        data_mode = True

    if cmd.upper() == "QUIT":
        break

client.close()