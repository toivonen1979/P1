import socket
import ssl

SERVER_ADDRESS, SERVER_PORT = '', 53
RESOLVER_HOST, RESOLVER_PORT = '1.1.1.1', 853


def send_message(message, sock):
    sock.send(message)
    data = sock.recv(4096)
    return data


def add_length(udp_payload):
    length = len(udp_payload)
    blength_lbl = length.to_bytes(2, byteorder='big')
    tcp_payload = b''.join([blength_lbl, udp_payload])
    return tcp_payload


def remove_length(tcp_payload):
    udp_payload = tcp_payload[2:]
    return udp_payload


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


# Create a UDP socket.
server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port.
server_address = (SERVER_ADDRESS, SERVER_PORT)
print('starting up on {} port {}'.format(*server_address))
server_sock.bind(server_address)

while True:
    print('\nwaiting to receive message')
    data, address = server_sock.recvfrom(4096)

    print('received {} bytes from {}'.format(
        len(data), address))
    print(data)

    if data:
        payload = add_length(data)
        conn = connect()
        response = send_message(payload, conn)
        conn.close()
        udp_response = remove_length(response)
        sent = server_sock.sendto(udp_response, address)
        print('sent {} bytes back to {}'.format(
            sent, address))
