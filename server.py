import socket
import threading

def handle_client(client_socket, client_address):
    print(f"Connected: {client_address}")
    
    while True:
        #          wait until get data    |  bytes → string
        message = client_socket.recv(1024).decode("utf-8")

        if not message:
            print("Client disconnected")
            break

        print(f"Received: {message}")
        
        server_message = f"Server received: {message}"
        client_socket.sendall(server_message.encode("utf-8"))
        
    client_socket.close()
  

    
def main():
    #AF_INET means IPv4
    #SOCK_STREAM means TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    HOST = "127.0.0.1"
    PORT = 5050

    #Reserve the address and port for the server.
    server.bind((HOST, PORT))
    server.listen()
    
    # Set a short accept timeout so the main loop can check for KeyboardInterrupt
    # (allows graceful shutdown instead of blocking forever on accept())
    server.settimeout(1.0)
    try:
        while True:
            try:
                client_socket, client_address = server.accept()
                
            # no incoming connection yet, keep waiting
            except socket.timeout:
                continue

            thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address),
                daemon=True
            )
            thread.start()

    except KeyboardInterrupt:
        print("\nServer stopped")

    finally:
        server.close()
    
if __name__ == "__main__":
    main()
