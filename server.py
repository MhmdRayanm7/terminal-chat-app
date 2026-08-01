import socket
import threading


def main():
    #AF_INET means IPv4
    #SOCK_STREAM means TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    HOST = "127.0.0.1"
    PORT = 5050

    #Reserve the address and port for the server.
    server.bind((HOST, PORT))
    server.listen()

    client_socket, client_address = server.accept()
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
    server.close()
    
if __name__ == "__main__":
    main()
