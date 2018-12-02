import socket
import ssl

SERVER_ADDRESS, SERVER_PORT = '', 53
RESOLVER_HOST, RESOLVER_PORT = '1.1.1.1', 853


def send_message(message, sock):
    sock.send(message)
    data = sock.recv(4096)
    return data


def connect():
    # CREATE SOCKET
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(100)

    # WRAP SOCKET
    context = ssl.create_default_context()
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations('ca-bundle.crt')

    wrappedsocket = context.wrap_socket(sock, server_hostname=RESOLVER_HOST)

    # CONNECT AND PRINT REPLY
    wrappedsocket.connect((RESOLVER_HOST, RESOLVER_PORT))
    print(wrappedsocket.getpeercert())

    # CLOSE SOCKET CONNECTION
    return wrappedsocket



# Create a TCP/IP socket.
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (SERVER_ADDRESS, SERVER_PORT)
print('starting up on {} port {}'.format(*server_address))
server_sock.bind(server_address)
server_sock.listen(1)
while True:
    print('waiting for a connection')
    connection, client_address = server_sock.accept()
    try:
        print('client connected:', client_address)
        while True:
            data = connection.recv(4096)
            print('received {!r}'.format(data))
            print('received {} bytes from {}'.format(
                len(data), client_address))
            print(data)
            if data:
                conn = connect()
                response = send_message(data, conn)
                connection.sendall(response)
            else:
                break
    finally:
        print('closing connection')
        connection.close()

