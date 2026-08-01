import socket
import threading


def main():
    #AF_INET means IPv4
    #SOCK_STREAM means TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    HOST = "127.0.0.1"
    PORT = 5050
    
    #client try to connect to server
    client_socket.connect((HOST, PORT))
    print("You have connected Successfully")
    

    
    while True:
        message = input("> ")

        #to quit
        if message.strip().lower() == "/quit":
            break
        
        #if press enter
        if not message.strip():
            continue
        
        client_socket.sendall(message.encode("utf-8"))

        #          wait until get data    |  bytes → string
        server_message = client_socket.recv(1024).decode("utf-8")
        print(f"Received: {server_message }")
        

    
    client_socket.close()

if __name__ == "__main__":
    main()

    

