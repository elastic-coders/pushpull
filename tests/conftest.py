import asyncio
import gc
from io import StringIO

import pytest


# COPIED FROM aiohttp #


@pytest.yield_fixture
def loop(request):
    #loop = asyncio.get_event_loop()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)
    #asyncio.set_event_loop(loop)

    yield loop

    is_closed = getattr(loop, 'is_closed')
    if is_closed is not None:
        closed = is_closed()
    else:
        closed = loop._closed
    if not closed:
        loop.call_soon(loop.stop)
        loop.run_forever()
        loop.close()
    gc.collect()
    asyncio.set_event_loop(None)


@pytest.mark.tryfirst
def pytest_pycollect_makeitem(collector, name, obj):
    if collector.funcnamefilter(name):
        if not callable(obj):
            return
        item = pytest.Function(name, parent=collector)
        if 'run_loop' in item.keywords:
            return list(collector._genfunctions(name, obj))


@pytest.mark.tryfirst
def pytest_pyfunc_call(pyfuncitem):
    """
    Run asyncio marked test functions in an event loop instead of a normal
    function call.
    """
    if 'run_loop' in pyfuncitem.keywords:
        funcargs = pyfuncitem.funcargs
        loop = funcargs['loop']
        testargs = {arg: funcargs[arg]
                    for arg in pyfuncitem._fixtureinfo.argnames}
        loop.run_until_complete(pyfuncitem.obj(**testargs))
        return True


def pytest_runtest_setup(item):
    if 'run_loop' in item.keywords and 'loop' not in item.fixturenames:
        # inject an event loop fixture for all async tests
        item.fixturenames.append('loop')

# end copy from aiohttp #


@pytest.yield_fixture
def websocket_cli(loop):

    from pushpull.websocket.client import challenge

    inp, out = StringIO(), StringIO()
    yield challenge('http://localhost:8080', 'test', inp, out, loop=loop), inp, out


@pytest.yield_fixture
def websocket_server(loop):

    # TODO
    yield None
