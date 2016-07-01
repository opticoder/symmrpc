# -*- coding: utf-8 -*-

import logging

log = logging.getLogger('symmrpc')

global_namespace_server = None
global_namespace_proxy = None
global_namespace_funcs = {}


def init_global_ns_server(send_msg):
    global global_namespace_server
    from server import SimpleRPCServer
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
