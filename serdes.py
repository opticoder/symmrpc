import msgpack

class SerDesMsgpack(object):
    def __init__(self):
        self.unpacker = msgpack.Unpacker()

    def serialize(self, msg):
        return msgpack.packb(msg)

    def deserialize(self, msg):
        self.unpacker.feed(msg)
        return self.unpacker

