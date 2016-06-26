# -*- coding: utf-8 -*-

import logging

log = logging.getLogger('symmrpc')


class Operation:
    call, result = range(2)


class SymmetricRPCClient(object):
    def __init__(self):
        self.callbacks = {}

    def is_call_finished(self, lifoqueue):
        if not lifoqueue.empty():
            val = lifoqueue.get()
            lifoqueue.put(val)
            if val == StopIteration:
                return True
            if val[0] == Operation.result:
                return True
        return False

    def call_func(self, func_name, orig_args, lifoqueue, send_message):
        callbacks = []
        self.callbacks = {}
        args = list(orig_args)
        for n in range(len(args)):
            log.debug('func %s arg %d type %s', func_name, n, type(args[n]))
            if hasattr(args[n], '__call__'):
                name = args[n].__name__
                self.callbacks[name] = args[n]
                args[n] = name
                callbacks.append(n)

        log.info('calling remote func %s %s', func_name, args)
        # FIXME: must be LifoQueue processing
        send_message((Operation.call, func_name, args, callbacks))
        while True:
            o = lifoqueue.get()
            if (o == StopIteration):
                return StopIteration
            elif (o[0] == Operation.result):
                # FIXME: process remained items for procedures (not functions!) callbacks
                log.debug('result=%s', o[1])
                return o[1]
            elif (o[0] == Operation.call):
                self.callbacks[o[1]](*o[2])
            # TODO: else error


class SymmetricRPCServer(object):
    def __init__(self):
        self.funcs = {}

    def register_function(self, func, func_name = None):
        if func_name is None:
            name = func.__name__
        else:
            name = func_name
        log.info('registered function %s with name %s', func, func_name)
        self.funcs[name] = func

    def received_message(self, o):
        print "received obj:", o
        if o[0] == Operation.call:
            for cb in o[3]:
                name = o[2][cb]
                import functools
                o[2][cb] = functools.partial(lambda name, *args: self.send_message((Operation.call, name, args)),
                                             name)
                log.debug("callback %s=%s", name, o[2][cb])
            func = self.funcs[o[1]]
            log.debug('requested worker call func %s name %s args=%s', func, o[1], o[2])
            result = func(*o[2])
            self.send_message((Operation.result, result))

    def send_message(self, msg):
        raise NotImplementedError
