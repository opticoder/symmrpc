import pytest
import sys
sys.path.append("../src")


import logging
log = logging.getLogger('symmrpc')
handler = logging.StreamHandler()
handler.setFormatter( logging.Formatter( ': %(levelname)s [%(funcName)s] %(message)s' ) )
log.addHandler( handler )
log.setLevel( logging.DEBUG )



def echo(m):
    return m

from_callback = None
def my_callback(m):
    global from_callback
    from_callback = m
    print('callback called', m, from_callback)
def do_callback(callback_func, m):
    global from_callback
    callback_func(m)
    print('from_callback=', from_callback)
    return from_callback


from protocol import SymmRPCError
def full_test(server, call, shutdown):
    with pytest.raises(SymmRPCError):
        call('wrong_func_name', 'abc')

    test_string = str(server.__class__)
    server.register_function(echo)
    assert call('echo', test_string) == test_string

    server.register_function(do_callback)
    call('do_callback', my_callback, 'abc1')
    assert from_callback == 'abc1'

    shutdown()


@pytest.fixture(scope="module")
def tester():
    return full_test
