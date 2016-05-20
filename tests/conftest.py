from io import StringIO

import pytest


@pytest.yield_fixture
def websocket_cli(event_loop):

    from pushpull.websocket.client import challenge

    inp, out = StringIO(), StringIO()
    yield challenge('http://localhost:8080', 'test', inp, out, loop=event_loop), inp, out


@pytest.yield_fixture
def websocket_server(event_loop):

    # TODO
    yield None
