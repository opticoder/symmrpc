import pytest
import ws
import server
import testing.ws

class WorkersWebsocketPool():
    def __init__(self):
        self.rpc = server.SimpleRPCServer(self.my_send)
        self.send_data = None

    def rpc_srv(self):
        return self.rpc

    def init(self, send_data):
        print('worker init')
        self.send_data = send_data
        return self.rpc.received_data

    def my_send(self, msg):
        self.send_data(msg)

    def open(self, host, port):
        self.pool = testing.ws.run_workers(host, port, 1, self.init)

    def stop(self):
        self.pool.terminate()

import serdes
class WorkersWebsocketProxy():
    def connect(self, host, port):
        self.proxy = ws.WorkerProxy(host, port, serdes.SerDesMsgpack)

    def call(self, name, *args):
        self.proxy.call_func(name, args)

@pytest.yield_fixture(scope="module")
def gevent_websocket_workers_pool():
    server = WorkersWebsocketPool()
    yield server
    server.stop()

@pytest.fixture(scope="module")
def gevent_websocket_workers_proxy():
    client = WorkersWebsocketProxy()
    return client



def undrcnstr_test_gevent_ws(gevent_websocket_workers_pool, gevent_websocket_workers_proxy):
    gevent_websocket_workers_pool.rpc_srv().register_function(echo)
    gevent_websocket_workers_pool.open('127.0.0.1', 8000)
    gevent_websocket_workers_proxy.connect('127.0.0.1', 8000)
    assert gevent_websocket_workers_proxy.call('echo', 'abc4') == 'abc4'
