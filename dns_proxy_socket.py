import socket
import ssl


HOST, PORT = '1.1.1.1', 853


def send_message(_message, sock):
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

    wrappedsocket = context.wrap_socket(sock, server_hostname=HOST)

    # CONNECT AND PRINT REPLY
    wrappedsocket.connect((HOST, PORT))
    print(wrappedsocket.getpeercert())

    # CLOSE SOCKET CONNECTION
    return wrappedsocket

message = b'\x00\x1c\x00B\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06google\x03com\x00\x00\x01\x00\x01'

conn = connect()
response = send_message(message, conn)
print(response)