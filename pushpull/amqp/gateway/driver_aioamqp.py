import logging
import asyncio

import aioamqp

from ... import config
from .driver_base import ExchangerBase

logger = logging.getLogger(__name__)


class Exchanger(ExchangerBase):

    async def __aenter__(self):
        logger.debug('connecting with role {}'.format(self.role))
        params = config.get_amqp_conn_params(self.url)
        params['login'] = params.pop('username')
        params['virtualhost'] = params.pop('virtual_host')
        self._transport, self._protocol = await aioamqp.connect(**params)
        # TODO: handle reconnect awaiting from self._conn
        self._chan = await self._protocol.channel()
        app_exchange_name = self.get_app_exchange_name()
        app_routing_key = self.get_app_routing_key()
        app_exchange_name = self.get_app_exchange_name()
        app_routing_key = self.get_app_routing_key()
        ws_exchange_name = self.get_ws_exchange_name()
        ws_routing_key = self.get_ws_routing_key()
        ws_routing_key_bcast = self.get_ws_routing_key(broadcast=True)
        await self._chan.exchange(app_exchange_name, 'direct', durable=True)
        await self._chan.exchange(ws_exchange_name, 'topic', durable=True)
        if self.role == self.ROLE_WS:
            receive_queue_name = '{}.{}'.format(ws_routing_key, self.client_id)
            await self._chan.queue(receive_queue_name, exclusive=True, durable=False)
            await self._chan.queue_bind(
                exchange_name=ws_exchange_name,
                queue_name=receive_queue_name,
                routing_key=ws_routing_key
            )
            await self._chan.queue_bind(
                exchange_name=ws_exchange_name,
                queue_name=receive_queue_name,
                routing_key=ws_routing_key_bcast
            )
            send_exchange_name, send_routing_key = app_exchange_name, app_routing_key
        if self.role == self.ROLE_APP:
            receive_queue_name = 'pushpull.app'
            await self._chan.queue(receive_queue_name, durable=True)
            await self._chan.queue_bind(
                exchange_name=app_exchange_name,
                queue_name=receive_queue_name,
                routing_key=app_routing_key
            )
            send_exchange_name, send_routing_key = ws_exchange_name, ws_routing_key
        logger.debug('connected ok')
        return (
            Sender(self._chan, send_exchange_name, send_routing_key),
            Receiver(self._chan, receive_queue_name)
        )

    async def __aexit__(self, exc_type, exc_value, traceback):
        logger.debug('closing connection and channel')
        try:
            await self._protocol.close()
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception('error closing')


class Sender:

    def __init__(self, channel, exchange_name, routing_key):
        self._chan = channel
        self._exchange_name = exchange_name
        self._routing_key = routing_key

    async def send(self, message):
        await self._chan.basic_publish(
            message,
            exchange_name=self._exchange_name,
            routing_key=self._routing_key
        )
        logger.debug('publishing message %r', message)


class Receiver:

    def __init__(self, channel, queue_name):
        self._channel = channel
        self._queue_name = queue_name
        self._fifo = asyncio.Queue(100)

    async def __call__(self, channel, body, envelope, properties):
        logger.debug('received message %r', body)
        try:
            self._fifo.put_nowait(body.decode())  # TODO: get encoding
        except asyncio.QueueFull:
            logger.warning('queue full')

    async def __aiter__(self):
        await self._channel.basic_consume(
            self,
            self._queue_name,
            no_ack=True,
        )
        return self

    async def __anext__(self):
        data = await self._fifo.get()
        if data is None:
            raise StopAsyncIteration
        return data
