# -*- coding: utf-8 -*-

import logging

log = logging.getLogger('symmrpc')

from symmrpc.protocol import SymmetricRPCServer
from symmrpc.serdes import SerDesMsgpack

global_namespace_server = None
global_namespace_proxy = None
global_namespace_funcs = {}

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


def init_global_ns_server(send_msg):
    global global_namespace_server
    global_namespace_server = SimpleRPCServer(send_msg)
    for name, func in global_namespace_funcs.items():
        global_namespace_server.register_function(func, name)
    log.info('Inited as server')
    return global_namespace_server.received_data


def remote(name=None):
    def wrap(func):
        global_namespace_funcs[func.__name__ if not name else name] = func
        def func_wrapper(*args):
            if global_namespace_proxy is None:
                log.debug('local call func %s %s', func.__name__, args)
                return func(*args)
            else:
                log.debug('rpc call func %s %s', func.__name__, args)
                return global_namespace_proxy.call_func(func.__name__, args)
        return func_wrapper
    return wrap
