# -*- coding: utf-8 -*-

import logging

log = logging.getLogger('symmrpc')


from ws4py.client.geventclient import WebSocketClient
import gevent
from gevent import queue
from symmrpc.protocol import SymmetricRPCClient
from symmrpc.serdes import SerDesMsgpack


class WorkerStream(WebSocketClient):
    def __init__(self, addr, serdes):
        WebSocketClient.__init__(self, addr, protocols=['http-only', 'chat'])
        self.result = None
        self.disconnected = False
        self.serdes = serdes()

    def closed(self, code, reason=None):
        print("Closed down", code, reason)
        self.disconnected = True
        if not self.result is None:
            # worker crash case or just disconnect
            self.result.put(StopIteration)
        # TODO: maybe to not change queues
        self.result = None

    def is_connected(self):
        #                log.debug('stream %d state: t %d d %d ct %d', n, self.streams[n].terminated,
        #                          self.streams[n].disconnected, self.streams[n].client_terminated)
        return not self.disconnected

    def received_message(self, msg):
        # TODO: check message.is_binary
        for msg in self.serdes.deserialize(msg.data):
            log.debug('received msg: %s', msg)
            self.result.put(msg)

    def set_queue(self, queue):
        self.result = queue

    def get_queue(self):
        return self.result

    def send_message(self, msg):
        self.send(self.serdes.serialize(msg), binary=True)



class WorkerProxy:
    def __init__(self, addr, port, serdes=SerDesMsgpack):
        # TODO: pooling
        self.serdes = serdes
        self.streams = []
        self.clients = []
        gevent.spawn(self.streams_connect, addr, port)

    def streams_connect(self, addr, port):
        def try_connect():
            stream = WorkerStream('ws://'+addr+':'+str(port)+'/ws', self.serdes)
            try:
                stream.connect()
                return stream
            except:
                return None

        while True:
            log.debug('looking for more streams')
            for n in range(len(self.streams)):
                if not self.streams[n].is_connected():
                    log.debug('trying to reconnect existing stream %d', n)
                    stream = try_connect()
                    if stream is not None:
                        self.streams[n] = stream
                        log.info('existing stream reconnected %d', n)
                    else:
                        break
            else:
                log.debug('trying to connect new stream %d', len(self.streams))
                stream = try_connect()
                if stream is not None:
                    log.info('new stream connected %d', len(self.streams))
                    self.streams.append(stream)
                    self.clients.append(SymmetricRPCClient())
                    continue
                else:
                    pass
            gevent.sleep(1)

    def find_ready_stream(self):
        while True:
            log.debug('try to find a ready stream')
            for n in range(len(self.streams)):
                log.debug('check for stream %d: obj %s result %s', n, self.streams[n].disconnected, self.streams[n].result)
                if self.streams[n].is_connected():
                    # TODO: split to two passes for performance reasons
                    lifoqueue = self.streams[n].get_queue()
                    if lifoqueue is None:
                        return n
                    if self.clients[n].is_call_finished(lifoqueue):
                        return n
            gevent.sleep(1)

    def call_func(self, func_name, orig_args):
        n = self.find_ready_stream()
        log.debug('got ready stream')
        lifoqueue = queue.Queue()
        self.streams[n].set_queue(lifoqueue)
        res = self.clients[n].call_func(func_name, orig_args, lifoqueue, self.streams[n].send_message)
        self.streams[n].set_queue(None)
        return res


def init_global_ns_proxy(addr, port, force_init=False, serdes=SerDesMsgpack):
    import symmrpc
    if symmrpc.global_namespace_proxy is not None:
        if not force_init:
            return
    symmrpc.global_namespace_proxy = WorkerProxy(addr, port, serdes)
    log.info('Inited as proxy')
