import logging
import asyncio

import aiohttp

from ..linereader import FdLineReader


logger = logging.getLogger(__name__)


async def challenge(url, name, fd_in, fd_out, loop=None):
    with aiohttp.ClientSession(loop=loop) as session:
        async with session.ws_connect('{}?name={}'.format(url, name)) as ws:
            logger.debug('opening websocket')
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
        elif msg.tp == aiohttp.MsgType.error:
            logger.error('ws connection closed with exception %s', ws.exception())
            return
