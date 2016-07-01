from protocol import SymmetricRPCServer, SymmetricRPCClient

class PlainRPCServer(SymmetricRPCServer):
    def __init__(self, send_data):
        super(PlainRPCServer, self).__init__()
        self.send_data = send_data

    def send_message(self, msg):
        self.send_data(msg)


class PlainRPCClient(SymmetricRPCClient):
    def __init__(self, send_data, recv_data):
        super(PlainRPCClient, self).__init__()
        self.send_data = send_data
        self.recv_data = recv_data

    def call(self, name, *args):
        return self.call_func(name, args, self.recv_data, self.send_data)
