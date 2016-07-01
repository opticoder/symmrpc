import socket
import threading
import server
from helpers import PlainRPCClient


class TCPRPCServer(server.SimpleRPCServer):
    def __init__(self):
        super(TCPRPCServer, self).__init__(self.my_send)
        self.sock = None
        self.conn = None
        self.t = threading.Thread(target=self.run)
        self.t.daemon = True # to avoid the hassle of server graceful shutdown

    def my_send(self, msg):
        self.conn.sendall(msg)

    def open(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(1)
        self.t.start()

    def run(self):
        self.conn, addr = self.sock.accept()
        print('Connected by', addr)
        while True:
            chunk = self.conn.recv(2048)
            if chunk == '':
                raise RuntimeError("socket connection broken")
            self.received_data(chunk)

import serdes
class TCPRPCClient(PlainRPCClient):
    def __init__(self):
        super(TCPRPCClient, self).__init__(self.my_send, self.my_receive)
        self.serdes = serdes.SerDesMsgpack()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        self.sock.connect((host, port))

    def my_send(self, msg):
        self.sock.sendall(self.serdes.serialize(msg))

    def my_receive(self):
        while True:
            chunk = self.sock.recv(2048)
            if chunk == '':
                raise RuntimeError("socket connection broken")
            return self.serdes.deserialize(chunk)


def test_tcp(tester):
    server = TCPRPCServer()
    client = TCPRPCClient()
    server.open('localhost', 5000)
    client.connect('localhost', 5000)
    def shutdown():
        # FIXME: close the server socket
        pass
    tester(server, client.call, shutdown)
