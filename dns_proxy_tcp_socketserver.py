import socketserver
import socket
import ssl


HOST, PORT = '1.1.1.1', 853

def send_message(message, sock):
    sock.send(message)
    data = sock.recv(4096)
    return data

def connect():
    # CREATE SOCKET
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('socket created')
    sock.settimeout(100)

    # WRAP SOCKET
    context = ssl.create_default_context()
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations('ca-bundle.crt')
    print('context created')

    wrappedSocket = context.wrap_socket(sock, server_hostname=HOST)
    print('wrappedsocket created')

    # CONNECT AND PRINT REPLY
    wrappedSocket.connect((HOST, PORT))
    print(wrappedSocket.getpeercert())

    # CLOSE SOCKET CONNECTION
    return wrappedSocket


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(4096)
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        conn = connect()
        response = send_message(self.data, conn)
        self.request.sendall(response)


if __name__ == "__main__":
    HOST, PORT = "localhost", 53

    # Create the server, binding to localhost on port 53
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
