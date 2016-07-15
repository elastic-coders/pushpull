import logging
import asyncio

import asynqp

from .driver_base import ExchangerBase
from ... import config

logger = logging.getLogger(__name__)


class Exchanger(ExchangerBase):

    async def __aenter__(self):
        logger.debug('connecting with role {}'.format(self.role))
        params = config.get_amqp_conn_params(self.url)
        self._conn = await asynqp.connect(**params)
        self._chan = await self._conn.open_channel()
        app_exchange_name = self.get_app_exchange_name()
        app_routing_key = self.get_app_routing_key()
        ws_exchange_name = self.get_ws_exchange_name()
        ws_routing_key = self.get_ws_routing_key()
        app_exchange = await self._chan.declare_exchange(app_exchange_name, 'fanout')
        ws_exchange = await self._chan.declare_exchange(ws_exchange_name, 'direct')
        if self.role == self.ROLE_WS:
            receive_queue_name = '{}.{}'.format(ws_routing_key, self.client_id)
            receive_queue = await self._chan.declare_queue(receive_queue_name)
            await receive_queue.bind(ws_exchange, ws_routing_key)
            send_exchange = app_exchange
            send_routing_key = app_routing_key
        if self.role == self.ROLE_APP:
            receive_queue = await self._chan.declare_queue('pushpull.app')
            await receive_queue.bind(app_exchange, app_routing_key)
            send_exchange = ws_exchange
            send_routing_key = ws_routing_key
        logger.debug('connected ok')
        return Sender(send_exchange, send_routing_key), Receiver(receive_queue)

    async def __aexit__(self, exc_type, exc_value, traceback):
        logger.debug('closing connection and channel')
        try:
            await self._chan.close()
            await self._conn.close()
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.error('error closing')


class Sender:

    def __init__(self, exchange, routing_key):
        self._exch = exchange
        self._routing_key = routing_key

    async def send(self, message):
        mesg = asynqp.Message(message)
        logger.debug('publishing message %r', mesg)
        self._exch.publish(mesg, self._routing_key)


class Receiver:

    def __init__(self, queue):
        self._amqp_queue = queue
        self._fifo = asyncio.Queue(100)

    def __call__(self, amqp_message):
        logger.debug('received message %r', amqp_message.body)
        try:
            self._fifo.put_nowait(amqp_message.body.decode(amqp_message.content_encoding))
        except asyncio.QueueFull:
            logger.warning('queue full')
        else:
            amqp_message.ack()

    def on_error(self, exc):
        logger.error('error received: %r', exc)
        self._fifo.put_nowait(None)

    async def __aiter__(self):
        await self._amqp_queue.consume(self)
        return self

    async def __anext__(self):
        data = await self._fifo.get()
        if data is None:
            raise StopAsyncIteration
        return data
