import asyncio
import logging

from .gateway.driver_aioamqp import Exchanger
from ..linereader import FdLineReader

logger = logging.getLogger(__name__)


async def challenge(name, fd_in, fd_out):
    async with Exchanger(name, Exchanger.ROLE_APP) as (amqp_sender, amqp_receiver):
        sender = send_from_fd_to_amqp(fd_in, amqp_sender)
        receiver = send_from_amqp_to_fd(amqp_receiver, fd_out)
        _, pending = await asyncio.wait([sender, receiver], return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()


async def send_from_fd_to_amqp(fd, sender):
    async for line in FdLineReader(fd):
        logger.debug('sending message %r', line)
        await sender.send(line)


async def send_from_amqp_to_fd(receiver, fd):
    async for msg in receiver:
        fd.write(msg)
