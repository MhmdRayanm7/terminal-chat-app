import socket  
import threading  


clients = []  # list to keep track of connected client sockets
usernames = {}  # map each client socket to its username
clients_lock = threading.Lock()  # lock to protect shared client data


def broadcast(message):
    # copy the list while holding the lock to avoid race conditions
    with clients_lock:
        connected_clients = clients.copy()

    # send the message to each client
    for connected_client in connected_clients:
        try:
            connected_client.sendall(message.encode("utf-8"))
        except OSError:
            # if sending fails, remove the client
            remove_client(connected_client)


def remove_client(client_socket):
    # remove the client and username safely
    with clients_lock:
        if client_socket in clients:
            clients.remove(client_socket)
        if client_socket in usernames:
            del usernames[client_socket]

    # close the socket to release resources
    client_socket.close()


def handle_client(client_socket, client_address):
    print(f"Connected: {client_address}")
    username = None

    try:
        # The first data received from a client is always its username.
        username = client_socket.recv(1024).decode("utf-8").strip()

        if not username:
            return

        with clients_lock:
            clients.append(client_socket)
            usernames[client_socket] = username

        broadcast(f"- {username} joined the chat *")

        while True:
        #          wait until get data    |  bytes → string
            message = client_socket.recv(1024).decode("utf-8")

            if not message:
                break

            command = message.strip().lower()

            if command.startswith("/users"):
                with clients_lock:
                    online_users = list(usernames.values())

                users_message = f"Online users: {', '.join(online_users)}"
                client_socket.sendall(users_message.encode("utf-8"))
                continue

            if command.startswith("/quit"):
                break

            formatted_message = f"{username}: {message}"
            print(f"Received from {client_address}: {formatted_message}")
            broadcast(formatted_message)

    except OSError:
        # ignore socket errors during receive
        pass

    finally:
        print(f"Disconnected: {client_address}")

        # Remove this user before notifying the remaining clients.
        remove_client(client_socket)

        if username:
            broadcast(f"- {username} left the chat *")


def main():
    host = "127.0.0.1"  # localhost
    port = 5050  # port to listen on

    # create a TCP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow Fast Restart
    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind((host, port))
    server.listen()
    server.settimeout(1.0)  # timeout to allow keyboard interrupt checks

    print(f"Server listening on {host}:{port}")

    try:
        while True:
            try:
                client_socket, client_address = server.accept()
            except socket.timeout:
                continue

            thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address),
                daemon=True
            )

            thread.start()

    except KeyboardInterrupt:
        # shutdown on Ctrl+C
        print("\nServer stopped")

    finally:
        server.close()


if __name__ == "__main__":
    main()
