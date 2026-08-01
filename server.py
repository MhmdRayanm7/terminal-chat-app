import socket  
import threading  


clients = []  # list to keep track of connected client sockets
clients_lock = threading.Lock()  # lock to protect access to clients list


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
    # remove the client from the list safely
    with clients_lock:
        if client_socket in clients:
            clients.remove(client_socket)

    # close the socket to release resources
    client_socket.close()


def handle_client(client_socket, client_address):
    print(f"Connected: {client_address}")

    # add client to the shared list
    with clients_lock:
        clients.append(client_socket)

    try:
        while True:
        #          wait until get data    |  bytes → string
            message = client_socket.recv(1024).decode("utf-8")

            if not message:
                break

            print(f"Received from {client_address}: {message}")
            broadcast(message)

    except OSError:
        # ignore socket errors during receive
        pass

    finally:
        print(f"Disconnected: {client_address}")
        remove_client(client_socket)


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