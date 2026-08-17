import socket
import select

HOST = "0.0.0.0"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen()

server.setblocking(False)

print("=" * 50)
print("SELECT()-BASED TCP SERVER")
print("=" * 50)
print(f"Server listening on {HOST}:{PORT}")

# List of sockets that select() should monitor
sockets_list = [server]

# Store client addresses
clients = {}


while True:

    # Monitor sockets for incoming data/connections
    readable, _, exceptional = select.select(
        sockets_list,
        [],
        sockets_list
    )

    for sock in readable:

        # If the server socket is readable,
        # it means a new client wants to connect
        if sock == server:

            client_socket, client_address = server.accept()

            client_socket.setblocking(False)

            sockets_list.append(client_socket)
            clients[client_socket] = client_address

            print(
                f"New connection from "
                f"{client_address[0]}:{client_address[1]}"
            )

        else:

            # Existing client sent data
            try:
                data = sock.recv(1024)

                # recv() returning empty means client disconnected
                if not data:
                    print(f"Client disconnected: {clients[sock]}")

                    sockets_list.remove(sock)
                    del clients[sock]
                    sock.close()

                    continue

                message = data.decode()

                print(
                    f"Received from {clients[sock]}: {message}"
                )

                # Echo message back to client
                response = f"Server received: {message}"

                sock.sendall(response.encode())

            except ConnectionResetError:

                print(f"Client forcibly disconnected: {clients[sock]}")

                sockets_list.remove(sock)
                del clients[sock]
                sock.close()

    # Handle exceptional sockets
    for sock in exceptional:

        print(f"Exception on socket: {clients.get(sock)}")

        if sock in sockets_list:
            sockets_list.remove(sock)

        if sock in clients:
            del clients[sock]

        sock.close()
