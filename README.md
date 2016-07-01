This RPC library is the result of inspiration from msgpack-rpc simplicity with performance, https://github.com/niligulmohar/python-symmetric-jsonrpc power and the real production needs for some of my projects.

# Main features
* Symmetry: server can invoke callback functions on client
* Efficiency: by using msgpack (but can be easily replaced by any other serializator)
* Able to be used in asynchronous as well as in threaded code (though some "modern" asynchronous frameworks such as asyncio makes to do some ambiguous tricks to get it worked asynchronously)

# Implementations
* Python 2/3
* C# client implementation is coming soon -)

# TODO
* Handling results from callbacks (now callbacks can not return values)
* Some documentation
* Examples (so far only the Python tests can be used as such)
* Travis CI builds (with coverage)
* Benchmarks and comparsions
* Other languages implementations
