import asyncio
import server
from helpers import PlainRPCClient


class AsyncioTCPRPCServer(server.SimpleRPCServer):
    def __init__(self):
        super(AsyncioTCPRPCServer, self).__init__(self.my_send)
        self.writer = None
        self.server = None

    def my_send(self, msg):
        print('Sending %s' % msg)
        # HACK
#        @asyncio.coroutine
        def send():
            print('Sending1')
            self.writer.write(msg)
#            print('Sending2')
        #    yield from self.writer.drain()
#        yield from \
        send()

    @asyncio.coroutine
    def handle(self, reader, writer):
        print('Connected to server')
        self.writer = writer
        while True:
            data = yield from reader.read(2048)
            print('server received')
            self.received_data(data)

    def open(self, host, port):
        loop = asyncio.get_event_loop()
        self.server = loop.run_until_complete(asyncio.start_server(self.handle, host, port, loop=loop))

    def close(self):
        self.server.close()


import serdes
class AsyncioTCPRPCClient(PlainRPCClient):
    def __init__(self):
        super(AsyncioTCPRPCClient, self).__init__(self.my_send, self.my_receive)
        self.serdes = serdes.SerDesMsgpack()
        self.reader = None
        self.writer = None
        self.loop = asyncio.get_event_loop()

    def connect(self, host, port):
        self.reader, self.writer = self.loop.run_until_complete(asyncio.open_connection(host, port, loop=self.loop))

    @asyncio.coroutine
    def call(self, name, *args):
        result = yield from self.loop.run_in_executor(None, super(AsyncioTCPRPCClient, self).call, name, *args)
        return result

    def my_send(self, msg):
        @asyncio.coroutine
        def send():
            self.writer.write(self.serdes.serialize(msg))
            yield from self.writer.drain()
        asyncio.run_coroutine_threadsafe(send(), self.loop)
        print('client Sent')

    def my_receive(self):
        @asyncio.coroutine
        def read():
            result = yield from self.reader.read(2048)
            return result
        future = asyncio.run_coroutine_threadsafe(read(), self.loop)
        return self.serdes.deserialize(future.result())


def test_asyncio_tcp(tester):
    server = AsyncioTCPRPCServer()
    client = AsyncioTCPRPCClient()
    server.open('localhost', 9000)
    client.connect('localhost', 9000)
    loop = asyncio.get_event_loop()

    def call(*args):
        @asyncio.coroutine
        def async_call(*args):
            result = yield from client.call(*args)
            return result
        return asyncio.run_coroutine_threadsafe(async_call(*args), loop).result()
    def shutdown():
        loop.stop()
        server.close()

    loop.run_in_executor(None, tester, server, call, shutdown)
    loop.run_forever()
