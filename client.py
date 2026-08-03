import socket  
import threading  


def receive_messages(client_socket):
    # keep incomplete data until new line arrive
    buffer = ""

    while True:
        try:
            # wait until get data from server
            received_data = client_socket.recv(1024)

            if not received_data:
                print("\nDisconnected from server")
                break

            # add new data to old incomplete data
            buffer += received_data.decode("utf-8")

            # print only complete messages
            while "\n" in buffer:
                # get one message and keep the rest in buffer
                message, buffer = buffer.split("\n", 1)
                print(f"\n{message}")
                print("> ", end="", flush=True)

        except OSError:
            # socket error or closed, stop receiving
            break


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
        print("Could not connect. Is the server running?")
        client_socket.close()
        return
    except OSError as error:
        print(f"Socket error: {error}")
        client_socket.close()
        return

    print("You have connected Successfully")

    # ask once then send username before normal messages
    username = input("Username: ").strip()

    while not username:
        print("Username cannot be empty.")
        username = input("Username: ").strip()

    # add new line to end of username
    client_socket.sendall(f"{username}\n".encode("utf-8"))

    # start a background thread to receive messages
    receive_thread = threading.Thread(
        target=receive_messages,
        args=(client_socket,),
        daemon=True,
    )

    receive_thread.start()

    try:
        while True:
            message = input("> ").strip()

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

    except KeyboardInterrupt:
        # handle Ctrl+C gracefully
        pass
    except OSError as error:
        print(f"Socket error: {error}")

    finally:
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        client_socket.close()


if __name__ == "__main__":
    main()

    

