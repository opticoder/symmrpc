try:
    import Queue
except ImportError:
    import queue as Queue
from helpers import PlainRPCServer, PlainRPCClient


def test_loopback(tester):
    queue = Queue.Queue()
    server = PlainRPCServer(lambda msg: queue.put(msg))
    client = PlainRPCClient(lambda msg: server.received_message(msg), lambda: [queue.get()])
    def shutdown():
        pass
    tester(server, client.call, shutdown)
