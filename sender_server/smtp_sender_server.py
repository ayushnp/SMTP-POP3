import socket

HOST = "127.0.0.1"
PORT = 2525

RECEIVER_HOST = "127.0.0.1"
RECEIVER_PORT = 3535


def forward_mail(sender, receiver, message_lines):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)  # Prevents infinite hang if receiver doesn't respond
    s.connect((RECEIVER_HOST, RECEIVER_PORT))

    def recv():
        resp = s.recv(1024).decode()
        print("Receiver SMTP Response:", resp.strip())
        return resp

    def send(cmd):
        s.send((cmd + "\r\n").encode())
        return recv()

    # Protocol Handshake
    recv()  # 220 greeting
    send("HELO sender-server")
    send(f"MAIL FROM:{sender}")
    send(f"RCPT TO:{receiver}")
    send("DATA")

    # Send Message Body
    for line in message_lines:
        s.send((line + "\r\n").encode())

    # End Data Mode
    s.send(b".\r\n")
    recv() # Expect 250 Message stored

    # Cleanly Close Connection
    send("QUIT")
    s.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"Sender SMTP Server listening on port {PORT}")

while True:
    sender_conn, client_address = server_socket.accept()
    print("Sender client connected:", client_address)

    sender_conn.send(b"220 Sender SMTP Server Ready\r\n")

    sender = ""
    receiver = ""
    data_mode = False
    message_lines = []

    try:
        while True:
            data = sender_conn.recv(1024).decode().strip()
            if not data:
                break

            print("C:", data)

            if data_mode:
                if data == ".":
                    try:
                        forward_mail(sender, receiver, message_lines)
                        sender_conn.send(b"250 Message forwarded\r\n")
                    except Exception as e:
                        print("Forwarding failed:", e)
                        sender_conn.send(
                            b"451 Requested action aborted: local error\r\n"
                        )

                    data_mode = False
                    message_lines = []
                else:
                    message_lines.append(data)

            elif data.startswith("HELO"):
                sender_conn.send(b"250 Hello\r\n")

            elif data.startswith("MAIL FROM"):
                # Clean the sender string to remove 'MAIL FROM:' prefix
                sender = data.split(":", 1)[1] if ":" in data else data
                sender_conn.send(b"250 OK\r\n")

            elif data.startswith("RCPT TO"):
                # Clean the receiver string
                receiver = data.split(":", 1)[1] if ":" in data else data
                sender_conn.send(b"250 OK\r\n")

            elif data == "DATA":
                data_mode = True
                message_lines = []
                sender_conn.send(b"354 End data with <CRLF>.<CRLF>\r\n")

            elif data == "QUIT":
                sender_conn.send(b"221 Bye\r\n")
                break

            else:
                sender_conn.send(b"500 Unknown command\r\n")

    except Exception as e:
        print("Error:", e)

    finally:
        sender_conn.close()
        print("Sender client disconnected")