from unittest import mock
import asyncio

import aiohttp
import pytest


@pytest.mark.asyncio
async def test_client_server_down(event_loop, websocket_cli):
    challenge, inp, out = websocket_cli
    with pytest.raises(aiohttp.errors.ClientOSError):
        await asyncio.wait_for(challenge, timeout=1, loop=event_loop)


@pytest.mark.skip(reason='TODO')
@pytest.mark.asyncio
async def test_client_server_send_one(event_loop, websocket_cli, websocket_server):
    challenge, inp, out = websocket_cli
    with mock.patch('pushpull.websocket.client.logger') as logger:
        inp.write('hey')
        inp.write('\n')
        await asyncio.wait_for(challenge, timeout=1, loop=event_loop)
        assert logger.debug.n_calls == 1
