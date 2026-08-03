import socket  
import threading  
from datetime import datetime

from terminal_colors import BLUE, CYAN, GRAY, GREEN, RED, YELLOW, color_text


clients = []  # list to keep track of connected client sockets
usernames = {}  # map each client socket to its username
clients_lock = threading.Lock()  # lock to protect shared client data
display_lock = threading.Lock()  # lock to stop threads from printing together
broadcast_lock = threading.Lock()  # lock to stop messages from mixing together


def display_message(message, color):
    # only one thread can display message at same time
    current_time = datetime.now().strftime("%H:%M")
    with display_lock:
        formatted_message = (
            f"{color_text(f'[{current_time}]', GRAY)} {color_text(message, color)}"
        )
        print(formatted_message)


def broadcast(message):
    # copy the list while holding the lock to avoid race conditions
    with clients_lock:
        connected_clients = clients.copy()

    disconnected_usernames = []
    # send the message to each client
    with broadcast_lock:
        for connected_client in connected_clients:
            try:
                # add new line so client know where message end
                connected_client.sendall(f"{message}\n".encode("utf-8"))
            except OSError:
                # if sending fails, remove the client
                removed_username = remove_client(connected_client)
                if removed_username:
                    disconnected_usernames.append(removed_username)

    for removed_username in disconnected_usernames:
        broadcast(f"- {removed_username} left the chat *")


def close_socket(socket_to_close):
    # shutdown and close socket safely
    try:
        socket_to_close.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    try:
        socket_to_close.close()
    except OSError:
        pass


def remove_client(client_socket):
    # remove the client and username safely
    removed_username = None
    with clients_lock:
        if client_socket in clients:
            clients.remove(client_socket)
        if client_socket in usernames:
            removed_username = usernames[client_socket]
            del usernames[client_socket]

    # close the socket to release resources
    close_socket(client_socket)

    return removed_username


def handle_client(client_socket, client_address):
    display_message(f"Connected: {client_address}", GREEN)
    username = None
    # keep incomplete data until new line arrive
    buffer = b""

    try:
        while True:
            # wait until get data from client
            received_data = client_socket.recv(1024)

            if not received_data:
                break

            # add new data to old incomplete data
            buffer += received_data

            # process only complete messages
            while b"\n" in buffer:
                # get one message and keep the rest in buffer
                message, buffer = buffer.split(b"\n", 1)
                message = message.decode("utf-8")

                # first complete message is the username
                if username is None:
                    username = message.strip()

                    with clients_lock:
                        username_is_used = username.casefold() in {
                            saved_username.casefold()
                            for saved_username in usernames.values()
                        }

                        if not username or username_is_used:
                            username_error = (
                                "Username cannot be empty."
                                if not username
                                else "Username is already used."
                            )
                        else:
                            clients.append(client_socket)
                            usernames[client_socket] = username

                    if not username or username_is_used:
                        client_socket.sendall(
                            f"{username_error}\n".encode("utf-8")
                        )
                        return

                    client_socket.sendall(b"USERNAME_ACCEPTED\n")
                    broadcast(f"- {username} joined the chat *")
                    continue

                command = message.strip().lower()

                # ignore empty messages
                if not message.strip():
                    continue

                # send online usernames only to this client
                if command == "/users":
                    with clients_lock:
                        online_users = list(usernames.values())

                    users_message = f"Online users: {', '.join(online_users)}"
                    # add new line so client can read complete message
                    client_socket.sendall(f"{users_message}\n".encode("utf-8"))
                    continue

                # stop this client when user quit
                if command == "/quit":
                    return

                formatted_message = f"{username}: {message}"
                display_message(
                    f"Received from {client_address}: {formatted_message}",
                    BLUE
                )
                broadcast(formatted_message)

    except (OSError, UnicodeDecodeError):
        # ignore socket errors during receive
        pass

    finally:
        display_message(f"Disconnected: {client_address}", CYAN)

        # remove this user before tell the other clients
        removed_username = remove_client(client_socket)

        if removed_username:
            broadcast(f"- {removed_username} left the chat *")


def main():
    host = "127.0.0.1"  # localhost
    port = 5050  # port to listen on

    # create a TCP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # stop two servers from using same port on Windows
    if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_EXCLUSIVEADDRUSE,
            1
        )
    else:
        # Allow Fast Restart
        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

    try:
        server.bind((host, port))
        server.listen()
        server.settimeout(1.0)  # timeout to allow keyboard interrupt checks
    except OSError as error:
        display_message(f"Could not start server: {error}", RED)
        close_socket(server)
        return

    display_message(f"Server listening on {host}:{port}", GREEN)

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
        display_message("Server stopped", YELLOW)

    finally:
        with clients_lock:
            connected_clients = clients.copy()

        for client_socket in connected_clients:
            remove_client(client_socket)

        close_socket(server)


if __name__ == "__main__":
    main()
