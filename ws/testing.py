# -*- coding: utf-8 -*-
"""This code is not a bit production-ready, just a pimped imitation of uWSGI server behavior
"""
import logging
import time
from multiprocessing import Process
from wsgiref.simple_server import make_server
from ws4py.websocket import WebSocket
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

log = logging.getLogger('symmrpc')


connected = False
class DummyWebSocketWSGIRequestHandler(WebSocketWSGIRequestHandler):
    def handle(self):
        global connected
        if not connected:
            connected = True
            WebSocketWSGIRequestHandler.handle(self)
        else:
            log.debug('busy by other client')

init_worker = None
class MyWebSocket(WebSocket):
    def opened(self):
        global init_worker
        log.debug('Socket opened')
        self.recv_data = init_worker(lambda x: self.send(x, binary=True))

    def received_message(self, message):
        # TODO: check message.is_binary
        self.recv_data(message.data)

    def closed(self, code, reason):
        log.debug('Socket closed %s %s', code, reason)


def start_worker(server, worker_num, init_woker_proc):
    global init_worker
    init_worker = init_woker_proc
    log.debug('starting worker %d', worker_num)
    try:
        server.initialize_websockets_manager()
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    log.debug('shut down worker %d', worker_num)


def master(count, host, port, init_worker_proc):
    worker_server = make_server(host, port, server_class=WSGIServer,
                                handler_class=DummyWebSocketWSGIRequestHandler,
                                app=WebSocketWSGIApplication(handler_cls=MyWebSocket))
    workers = [None] * count
    for i in range(count):
        workers[i] = Process(target=start_worker, args=(worker_server, i + 1, init_worker_proc))
        workers[i].start()

    while True:
        time.sleep(1)
        for i in range(count):
            if not workers[i].is_alive():
                log.debug('worker %d is dead', (i + 1))
                workers[i] = Process(target=start_worker, args=(worker_server, i + 1, init_worker_proc))
                workers[i].start()


def run_workers(host, port, count, init_worker_proc):
    Process(target=master, args=(count, host, port, init_worker_proc)).start()
