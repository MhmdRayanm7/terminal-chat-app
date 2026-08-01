import socket
import threading


def main():
    #AF_INET means IPv4
    #SOCK_STREAM means TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    HOST = "127.0.0.1"
    PORT = 5050

    server.bind((HOST, PORT))
    server.listen()

    client_socket, client_address = server.accept()
    print(f"Connected: {client_address}")

    client_socket.close()
    server.close()
    
if __name__ == "__main__":
    main()
