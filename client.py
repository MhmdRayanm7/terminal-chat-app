import socket  
import threading  


def receive_messages(client_socket):

    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")

            if not message:
                print("\nDisconnected from server")
                break

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
    client_socket.connect((HOST, PORT))
    print("You have connected Successfully")

    # Ask once, then send the username before any normal chat message.
    username = input("Username: ").strip()

    while not username:
        print("Username cannot be empty.")
        username = input("Username: ").strip()

    client_socket.sendall(username.encode("utf-8"))

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
                break

            # ignore empty messages
            if not message:
                continue

            #         wait until get data |  bytes → string
            client_socket.sendall(message.encode("utf-8"))

    except KeyboardInterrupt:
        # handle Ctrl+C gracefully
        pass

    finally:
        client_socket.close()


if __name__ == "__main__":
    main()

    

