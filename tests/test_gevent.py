import gevent
import gevent.socket
import gevent.server
import server
from helpers import PlainRPCClient


class GeventTCPRPCServer(server.SimpleRPCServer):
    def __init__(self):
        super(GeventTCPRPCServer, self).__init__(self.my_send)
        self.conn = None
        self.server = None

    def my_send(self, msg):
        self.conn.sendall(msg)

    def handle(self, socket, addr):
        self.conn = socket
        print('Connected by', addr)
        while True:
            try:
                chunk = socket.recv(2048)
                if chunk == '':
                    raise RuntimeError("socket connection broken")
                self.received_data(chunk)
            except:
                pass

    def open(self, host, port):
        self.server = gevent.server.StreamServer((host, port), self.handle)
        self.server.start()

    def run(self):
        self.server.serve_forever()

    def close(self):
        self.server.stop()


import serdes
class GeventTCPRPCClient(PlainRPCClient):
    def __init__(self):
        super(GeventTCPRPCClient, self).__init__(self.my_send, self.my_receive)
        self.serdes = serdes.SerDesMsgpack()

    def connect(self, host, port):
        self.sock = gevent.socket.create_connection((host, port))

    def my_send(self, msg):
        self.sock.sendall(self.serdes.serialize(msg))

    def my_receive(self):
        while True:
            chunk = self.sock.recv(2048)
            if chunk == '':
                raise RuntimeError("socket connection broken")
            return self.serdes.deserialize(chunk)


def test_gevent_tcp(tester):
    server = GeventTCPRPCServer()
    client = GeventTCPRPCClient()
    server.open('localhost', 9000)
    client.connect('localhost', 9000)

    def shutdown():
        server.close()

    gevent.spawn(tester, server, client.call, shutdown)
    server.run()
