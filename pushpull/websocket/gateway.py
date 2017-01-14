"""
Pushpull websocket server
"""
import logging
import asyncio
import random

import aiohttp
import aiohttp.web

from ..amqp.gateway.driver_aioamqp import Exchanger
from .. import config
from ..amqp import auth
from .auth import decode_auth_querystring_param

logger = logging.getLogger(__name__)


async def websocket_rabbitmq_gateway(request):
    authorization = decode_auth_querystring_param(request.GET)
    try:
        # TODO: reuse amqp channel: here we open one, we close it and then we reopen another one with the
        # Exchanger a few lines down
        user_info = await auth.get_user_info(authorization)
    except auth.NotAuthorized as exc:
        raise aiohttp.web_exceptions.HTTPUnauthorized() from exc
    except auth.NotAllowed as exc:
        raise aiohttp.web_exceptions.HTTPForbidden() from exc
    except auth.AuthTimeout as exc:
        logger.warning('auth backend timeout')
        raise aiohttp.web_exceptions.HTTPInternalServerError(text='auth backend timeout') from exc
    else:
        name = user_info.id
    ws = aiohttp.web.WebSocketResponse()
    client_id = request.GET.get('client-id')
    if not client_id:
        client_id = str(random.randint(1, 100))
        logger.warning('client-id not supplied by client: using random %s', client_id)
    logger.info('websocket connection open for %s and client id %s', name, client_id)
    try:
        await ws.prepare(request)
        async with Exchanger(name, Exchanger.ROLE_WS, client_id=client_id) as (amqp_sender, amqp_receiver):
            send_coro = send_from_amqp_to_websocket(amqp_receiver, ws)
            receive_coro = send_from_websocket_to_amqp(ws, amqp_sender)
            ping_coro = send_ping_to_websocket(ws, config.get_ws_autoping_timeout())
            done, pending = await asyncio.wait(
                [receive_coro, send_coro, ping_coro],
                return_when=asyncio.FIRST_COMPLETED
            )
            logger.info('client id %s exiting due to done coroutines %r', client_id, done)
            for coro in pending:
                logger.warning('client id %s cancelling pending coroutine %r', client_id, coro)
                coro.cancel()
            for coro in done:
                result = coro.result()
                logger.info('client id %s coroutine %r done, result: %r', client_id, coro, result)
    except Exception:
        logger.exception('client id %s exception while handling request', client_id)
    finally:
        logger.debug('client id %s websocket connection closing', client_id)
        await ws.close()
        return ws


async def send_from_websocket_to_amqp(ws, sender):
    async for msg in ws:
        if msg.tp == aiohttp.MsgType.text:
            logger.debug('got data: %s', msg.data)
            await sender.send(msg.data)
        elif msg.tp == aiohttp.MsgType.error:
            logger.error('ws connection closed with exception %s', ws.exception())
            return


async def send_from_amqp_to_websocket(receiver, ws):
    async for data in receiver:
        ws.send_str(data)
        # await ws._writer.writer.drain()


async def send_ping_to_websocket(ws, timeout):
    while True:
        logger.debug('sending ping to ws %r', ws)
        ws.ping()
        await asyncio.sleep(timeout)


async def echo_websocket(ws):
    """For testing only """
    async for msg in ws:
        if msg.tp == aiohttp.MsgType.text:
            logger.debug('echoing data: %s', msg.data)
            ws.send_str(msg.data)
        elif msg.tp == aiohttp.MsgType.error:
            logger.error('ws connection closed with exception %s', ws.exception())
            return
