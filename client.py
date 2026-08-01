import socket
import threading


def main():
    #AF_INET means IPv4
    #SOCK_STREAM means TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    HOST = "127.0.0.1"
    PORT = 5050
    
    client_socket.connect((HOST, PORT))
    print("You have connected Successfully")
    client_socket.close()

if __name__ == "__main__":
    main()

    

