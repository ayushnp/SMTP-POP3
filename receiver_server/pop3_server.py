import os
import socket

HOST = "127.0.0.1"
PORT = 1100

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAILBOX_DIR = os.path.join(BASE_DIR, "..", "mailboxes")

users = {
    "ayush": "1234"
}

pop_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pop_server.bind((HOST, PORT))
pop_server.listen(5)

print(f"POP3 server listening on port {PORT}")

while True:
    client_conn, addr = pop_server.accept()
    print("Client connected:", addr)

    client_conn.send(b"+OK POP3 server ready\r\n")

    user = None
    authenticated = False

    try:
        while True:
            data = client_conn.recv(1024).decode().strip()
            if not data:
                break

            print("C:", data)
            cmd = data.split()

            if cmd[0] == "USER":
                if cmd[1] in users:
                    user = cmd[1]
                    client_conn.send(b"+OK User accepted\r\n")
                else:
                    client_conn.send(b"-ERR Invalid user\r\n")

            elif cmd[0] == "PASS":
                if user and users[user] == cmd[1]:
                    authenticated = True
                    client_conn.send(b"+OK Auth successful\r\n")
                else:
                    client_conn.send(b"-ERR Auth failed\r\n")

            elif cmd[0] == "LIST":
                if not authenticated:
                    client_conn.send(b"-ERR Authenticate first\r\n")
                    continue

                inbox = os.path.join(MAILBOX_DIR, user, "inbox.txt")

                if not os.path.exists(inbox):
                    client_conn.send(b"+OK 0 messages\r\n")
                else:
                    with open(inbox, "r") as f:
                        mails = [m for m in f.read().split("---\n") if m.strip()]
                        client_conn.send(f"+OK {len(mails)} messages\r\n".encode())

            elif cmd[0] == "RETR":
                if not authenticated:
                    client_conn.send(b"-ERR Authenticate first\r\n")
                    continue

                index = int(cmd[1]) - 1
                inbox = os.path.join(MAILBOX_DIR, user, "inbox.txt")

                if not os.path.exists(inbox):
                    client_conn.send(b"-ERR Mailbox empty\r\n")
                    continue

                with open(inbox, "r") as f:
                    mails = [m for m in f.read().split("---\n") if m.strip()]

                if index < 0 or index >= len(mails):
                    client_conn.send(b"-ERR No such message\r\n")
                else:
                    client_conn.send(b"+OK Message follows\r\n")
                    client_conn.send((mails[index] + "\r\n.\r\n").encode())

            elif cmd[0] == "QUIT":
                client_conn.send(b"+OK Bye\r\n")
                break

            else:
                client_conn.send(b"-ERR Unknown command\r\n")

    except Exception as e:
        print("Client error:", e)

    finally:
        client_conn.close()
        print("Client disconnected")
