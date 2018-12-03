import threading
import socket
import ssl
import os
from time import sleep


SERVER_ADDRESS, SERVER_PORT = os.environ.get('SERVER_ADDRESS', ''), int(os.environ.get('SERVER_PORT', '53'))
RESOLVER_HOST, RESOLVER_PORT = os.environ.get('RESOLVER_HOST', '8.8.8.8'), int(os.environ.get('RESOLVER_PORT', '853'))
RETRY_TIMEOUT = 2


def add_length(udp_payload):
    length = len(udp_payload)
    blength_lbl = length.to_bytes(2, byteorder='big')
    tcp_payload = b''.join([blength_lbl, udp_payload])
    return tcp_payload


def remove_length(tcp_payload):
    udp_payload = tcp_payload[2:]
    return udp_payload


def tls_connect():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.400)
    context = ssl.create_default_context()
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations('ca-bundle.crt')
    wrappedsocket = context.wrap_socket(sock, server_hostname=RESOLVER_HOST)
    while True:
        try:
            wrappedsocket.connect((RESOLVER_HOST, RESOLVER_PORT))
            break
        except OSError:
            print('Connection failed. Retrying after {} s'.format(RETRY_TIMEOUT))
            sleep(RETRY_TIMEOUT)
    return wrappedsocket


def send_message(message, sock):
    sock.send(message)
    data = sock.recv(4096)
    return data


class TCPproxy(threading.Thread):
    def __init__(self, server_address):
        """Initialize the thread"""
        threading.Thread.__init__(self)
        self.server_address = server_address

    def run(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(self.server_address)
        server_sock.listen(1)
        while True:
            print('waiting for a TCP connection')
            connection, client_address = server_sock.accept()
            try:
                print('client connected:', client_address)
                while True:
                    data = connection.recv(4096)
                    print('received {} bytes from {}'.format(
                        len(data), client_address))
                    if data:
                        with tls_connect() as tls_conn:
                            response = send_message(data, tls_conn)
                        connection.sendall(response)
                    else:
                        break
            finally:
                print('closing connection')
                connection.close()


class UDPproxy (threading.Thread):
    def __init__(self, server_address):
        """Initialize the thread"""
        threading.Thread.__init__(self)
        self.server_address = server_address

    def run(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_sock.bind(self.server_address)
        while True:
            print('\nwaiting to receive message')
            data, address = server_sock.recvfrom(4096)
            print('received {} bytes from {}'.format(
                len(data), address))
            if data:
                payload = add_length(data)
                tls_conn = tls_connect()
                response = send_message(payload, tls_conn)
                udp_response = remove_length(response)
                sent = server_sock.sendto(udp_response, address)
                print('sent {} bytes back to {}'.format(
                    sent, address))


def main():
    thread_udp = UDPproxy((SERVER_ADDRESS, SERVER_PORT))
    thread_udp.start()
    thread_tcp = TCPproxy((SERVER_ADDRESS, SERVER_PORT))
    thread_tcp.start()


if __name__ == "__main__":
    main()
