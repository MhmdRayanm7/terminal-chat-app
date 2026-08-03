import socket  
import threading  
from datetime import datetime

from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.patch_stdout import patch_stdout
from terminal_colors import BLUE, CYAN, GRAY, GREEN, RED, RESET, YELLOW, color_text


display_lock = threading.Lock()  # lock to stop threads from printing together


def format_chat_message(username, message):
    # get current time when message display
    current_time = datetime.now().strftime("%H:%M")
    return f"{GRAY}[{current_time}]{RESET} {BLUE}{username}{RESET}\n{message}"


def format_system_message(message):
    return color_text(message, CYAN)


def display_message(message):
    # only one thread can display message at same time
    with display_lock:
        # ANSI make prompt toolkit understand colors instead of print them as text
        print_formatted_text(ANSI(f"\n{message}"))


def close_socket(client_socket):
    # shutdown and close socket safely
    try:
        client_socket.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    try:
        client_socket.close()
    except OSError:
        pass


def receive_line(client_socket):
    # receive first complete line and keep extra data
    buffer = b""
    while b"\n" not in buffer:
        received_data = client_socket.recv(1024)
        if not received_data:
            return None, buffer
        buffer += received_data

    message, buffer = buffer.split(b"\n", 1)
    return message.decode("utf-8"), buffer


def receive_messages(client_socket, buffer=b""):
    # keep incomplete data until new line arrive

    while True:
        try:
            # wait until get data from server
            received_data = client_socket.recv(1024)

            if not received_data:
                display_message(format_system_message("- Server disconnected *"))
                break

            # add new data to old incomplete data
            buffer += received_data

            # print only complete messages
            while b"\n" in buffer:
                # get one message and keep the rest in buffer
                message, buffer = buffer.split(b"\n", 1)
                message = message.decode("utf-8")

                # system messages start with - and command result starts with Online users
                if message.startswith("- "):
                    formatted_message = format_system_message(message)
                elif message.startswith("Online users:"):
                    formatted_message = color_text(message, YELLOW)
                elif ": " in message:
                    username, chat_message = message.split(": ", 1)
                    formatted_message = format_chat_message(username, chat_message)
                else:
                    formatted_message = color_text(message, RED)

                display_message(formatted_message)

        except (OSError, UnicodeDecodeError):
            # socket error or closed, stop receiving
            break


def input_and_send_messages(client_socket):
    session = PromptSession()

    while True:
        # patch stdout keep new messages above current input
        with patch_stdout():
            message = session.prompt(
                ANSI(f"{GREEN}Message › {RESET}")
            ).strip()

        #to quit
        if message.lower().strip() == "/quit":
            # send quit with new line before close
            client_socket.sendall(f"{message}\n".encode("utf-8"))
            break

        # ignore empty messages
        if not message:
            continue

        # add new line then encode and send message
        client_socket.sendall(f"{message}\n".encode("utf-8"))


def main():
    #AF_INET means IPv4
    #SOCK_STREAM means TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    HOST = "127.0.0.1"
    PORT = 5050
    
    #client try to connect to server
    try:
        client_socket.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(color_text("Could not connect. Is the server running?", RED))
        close_socket(client_socket)
        return
    except OSError as error:
        print(color_text(f"Socket error: {error}", RED))
        close_socket(client_socket)
        return

    print(color_text("You have connected Successfully", GREEN))
    print(color_text("─" * 40, GRAY))

    # ask once then send username before normal messages
    try:
        username = input("Username: ").strip()

        while not username:
            print("Username cannot be empty.")
            username = input("Username: ").strip()

        # add new line to end of username
        client_socket.sendall(f"{username}\n".encode("utf-8"))

        # wait until server accept or reject username
        username_response, buffer = receive_line(client_socket)
    except (KeyboardInterrupt, EOFError):
        close_socket(client_socket)
        return
    except (OSError, UnicodeDecodeError) as error:
        display_message(color_text(f"Socket error: {error}", RED))
        close_socket(client_socket)
        return

    if username_response != "USERNAME_ACCEPTED":
        error_message = username_response or "Server disconnected."
        display_message(color_text(error_message, RED))
        close_socket(client_socket)
        return

    # start a background thread to receive messages
    receive_thread = threading.Thread(
        target=receive_messages,
        args=(client_socket, buffer),
        daemon=True,
    )

    receive_thread.start()

    try:
        input_and_send_messages(client_socket)

    except (KeyboardInterrupt, EOFError):
        # handle Ctrl+C gracefully
        pass
    except OSError as error:
        display_message(color_text(f"Socket error: {error}", RED))

    finally:
        display_message(color_text("─" * 40, GRAY))
        close_socket(client_socket)


if __name__ == "__main__":
    main()

    
