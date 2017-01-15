import asyncio
import logging

from .gateway.driver_aioamqp import Exchanger
from .rpc.driver_aioamqp import RPC
from . import auth

from ..linereader import FdLineReader

logger = logging.getLogger(__name__)


async def challenge(url, user_id, fd_in, fd_out):
    async with Exchanger(user_id, Exchanger.ROLE_APP, url=url) as (amqp_sender, amqp_receiver):
        pending = [
            asyncio.ensure_future(coro) for coro in [
                send_from_fd_to_amqp(fd_in, amqp_sender),
                send_from_amqp_to_fd(amqp_receiver, fd_out)
            ]
        ]
        _, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()


async def authenticate(url, authenticator):
    async with RPC(RPC.ROLE_APP, url=url) as (amqp_sender, amqp_receiver):
        async for message in amqp_receiver:
            authorization = auth.decode_authorization_request(message.body)
            user = await authenticator(authorization)
            if user is None:
                logger.info('sending auth failure on auth %r', authorization)
                await amqp_sender.send(auth.encode_authorization_error_reply(),
                                       routing_key=message.reply_to,
                                       correlation_id=message.correlation_id)
            else:
                logger.info('sending auth success on auth %r for user %r', authorization, user)
                await amqp_sender.send(auth.encode_authorization_reply(*user),
                                       routing_key=message.reply_to,
                                       correlation_id=message.correlation_id)


async def send_from_fd_to_amqp(fd, sender):
    async for line in FdLineReader(fd):
        if line:
            logger.debug('sending message %r', line)
            await sender.send(line)


async def send_from_amqp_to_fd(receiver, fd):
    async for msg in receiver:
        fd.write(msg)
