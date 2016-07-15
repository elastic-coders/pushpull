import logging
import asyncio
import urllib.parse

import aiohttp

from ..linereader import FdLineReader
from .auth import encode_auth_querystring_param

logger = logging.getLogger(__name__)


async def challenge(url, token, fd_in, fd_out, loop=None):
    with aiohttp.ClientSession(loop=loop) as session:
        auth_params = encode_auth_querystring_param(token)
        url_parts = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(url_parts.query)
        query.update(auth_params)
        url_parts = list(url_parts)
        url_parts[4] = urllib.parse.urlencode(query)
        url = urllib.parse.urlunparse(url_parts)
        async with session.ws_connect(url, headers={'Origin': 'localhost'}) as ws:
            logger.debug('opening websocket')
            if logger.isEnabledFor(logging.DEBUG):
                for header in ('Access-Control-Allow-Origin', 'Access-Control-Allow-Credentials',
                               'Access-Control-Allow-Methods', 'Access-Control-Allow-Headers',
                               'Access-Control-Expose-Headers'):
                    logger.debug('CORS header {} origin: {!r}'.format(header, ws._response.headers.get(header)))
            sender = send_from_fd_to_ws(fd_in, ws, loop=loop)
            receiver = send_from_ws_to_fd(ws, fd_out)
            done, pending = await asyncio.wait([sender, receiver], return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
            logger.debug('closing websocket')
            # await ws.close()


async def send_from_fd_to_ws(fd, ws, loop=None):
    async for line in FdLineReader(fd, loop=loop):
        logger.debug('sending line from fd to ws %r', line)
        ws.send_str(line)
        await ws._writer.writer.drain()


async def send_from_ws_to_fd(ws, fd):
    async for msg in ws:
        if msg.tp == aiohttp.MsgType.text:
            logger.debug('sending data from ws to fd: %s', msg.data)
            fd.write(msg.data)
            fd.flush()
        elif msg.tp == aiohttp.MsgType.error:
            logger.error('ws connection closed with exception %s', ws.exception())
            return
