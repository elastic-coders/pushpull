from io import StringIO

import pytest


@pytest.yield_fixture
def websocket_cli(event_loop, unused_tcp_port):
    # TODO use server port somehow
    from pushpull.websocket.client import challenge
    inp, out = StringIO(), StringIO()
    yield challenge('http://127.0.0.1:{}'.format(unused_tcp_port), 'test', inp, out, loop=event_loop), inp, out


@pytest.yield_fixture
def websocket_server(event_loop):
    # TODO
    yield None
