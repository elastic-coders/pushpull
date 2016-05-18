import logging
import asyncio

import aiohttp

from ..linereader import FdLineReader


logger = logging.getLogger(__name__)


async def challenge(url, fd_in, fd_out):
    with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            logger.debug('opening websocket')
            await send_from_fd_to_ws(fd_in, ws)
            return
            sender = asyncio.ensure_future(send_from_fd_to_ws(fd_in, ws))
            receiver = asyncio.ensure_future(send_from_ws_to_fd(fd_out, ws))
            asyncio.gather(sender, receiver)
            logger.debug('closing websocket')
            # await ws.close()


async def send_from_fd_to_ws(fd, ws):
    async for line in FdLineReader(fd):
        logger.debug('sending message %r', line)
        ws.send_str(line)
        await ws._writer.writer.drain()


async def send_from_ws_to_fd(ws, fd):
    async for msg in ws:
        if msg.tp == aiohttp.MsgType.text:
            logger.debug('got data: %s', msg.data)
            fd.write(msg.data)
        elif msg.tp == aiohttp.MsgType.error:
            logger.error('ws connection closed with exception %s', ws.exception())
            return
