from unittest import mock
import asyncio

import aiohttp
import pytest


@pytest.mark.run_loop
async def test_client_server_down(loop, websocket_cli):
    challenge, inp, out = websocket_cli
    with pytest.raises(aiohttp.errors.ClientOSError):
        await asyncio.wait_for(challenge, timeout=1, loop=loop)


@pytest.mark.skip(reason='TODO')
@pytest.mark.run_loop
async def test_client_server_send_one(loop, websocket_cli, websocket_server):
    challenge, inp, out = websocket_cli
    with mock.patch('pushpull.websocket.client.logger') as logger:
        inp.write('hey')
        inp.write('\n')
        await asyncio.wait_for(challenge, timeout=1, loop=loop)
        assert logger.debug.n_calls == 1
