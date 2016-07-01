# -*- coding: utf-8 -*-

from protocol import SymmetricRPCServer
from serdes import SerDesMsgpack


class SimpleRPCServer(SymmetricRPCServer):
    def __init__(self, send_data, serdes=SerDesMsgpack):
        super(SimpleRPCServer, self).__init__()
        self.send_data = send_data
        self.serdes = serdes()

    def send_message(self, msg):
        self.send_data(self.serdes.serialize(msg))

    def received_data(self, msg):
        for params in self.serdes.deserialize(msg):
            super(SimpleRPCServer, self).received_message(params)
