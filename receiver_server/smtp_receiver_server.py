import socket
import os

HOST = "127.0.0.1"
PORT = 3535

# Absolute path handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAILBOX_DIR = os.path.join(BASE_DIR, "..", "mailboxes")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen(5)

print(f"Receiver SMTP Server running on port {PORT}")

while True:
    client_server, addr = server.accept()
    print(f"Client {addr} connected to Receiver server")


    client_server.settimeout(30)

    client_server.send(b"220 Receiver SMTP Server Ready\r\n")

    sender = ""
    receiver = ""
    data_mode = False
    message_lines = []

    try:
        while True:
            data = client_server.recv(1024).decode().strip()
            if not data:
                break

            print("C:", data)

            if data_mode:
                if data == ".":
                    user_dir = os.path.join(MAILBOX_DIR, receiver)
                    os.makedirs(user_dir, exist_ok=True)

                    with open(os.path.join(user_dir, "inbox.txt"), "a") as f:
                        f.write("FROM: " + sender + "\n")
                        f.write("\n".join(message_lines))
                        f.write("\n---\n")

                    client_server.send(b"250 Message stored\r\n")
                    data_mode = False
                    message_lines = []
                else:
                    message_lines.append(data)


            elif data.startswith("HELO"):
                client_server.send(b"250 HELLO\r\n")

            elif data.startswith("MAIL FROM"):
                sender = data
                client_server.send(b"250 OK\r\n")

            elif data.startswith("RCPT TO"):
                receiver = data.split(":")[1].split("@")[0]
                client_server.send(b"250 OK\r\n")

            elif data == "DATA":
                data_mode = True
                message_lines = []
                client_server.send(b"354 End data with <CRLF>.<CRLF>\r\n")

            elif data == "QUIT":
                client_server.send(b"221 BYE\r\n")
                break

            else:
                client_server.send(b"500 Unknown command\r\n")


    except socket.timeout:
        print(f"Client {addr} timed out")
        try:
            client_server.send(b"421 Timeout\r\n")
        except:
            pass
    except Exception as e:
        print("Client error:", e)

    finally:
        client_server.close()
        print("Client disconnected")
