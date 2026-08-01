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
    while True:
        client_socket, client_address = server.accept()
        thread = threading.Thread(
        target=handle_client,
        args=(client_socket,client_address)
        )
        thread.start()


    
if __name__ == "__main__":
    main()
