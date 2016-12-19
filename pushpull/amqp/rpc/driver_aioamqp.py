import logging
import asyncio
from collections import namedtuple

import aioamqp

from ... import config
from .driver_base import RPCBase

logger = logging.getLogger(__name__)


class RPC(RPCBase):

    async def __aenter__(self):
        params = config.get_amqp_conn_params(self.url)
        params['login'] = params.pop('username')
        params['virtualhost'] = params.pop('virtual_host')
        self._transport, self._protocol = await aioamqp.connect(**params)
        # TODO: handle reconnect awaiting from self._conn
        self._chan = await self._protocol.channel()
        app_exchange_name = self.get_app_exchange_name()
        app_routing_key = self.get_app_routing_key()
        await self._chan.exchange(app_exchange_name, 'direct')
        if self.role == self.ROLE_WS:
            result = await self._chan.queue('', exclusive=True, durable=False)
            receive_queue_name = result['queue']
            send_exchange_name, send_routing_key, reply_to = app_exchange_name, app_routing_key, receive_queue_name
        if self.role == self.ROLE_APP:
            receive_queue_name = 'pushpull.rpc'
            await self._chan.queue(receive_queue_name, durable=True)
            await self._chan.queue_bind(
                exchange_name=app_exchange_name,
                queue_name=receive_queue_name,
                routing_key=app_routing_key
            )
            send_exchange_name, send_routing_key, reply_to = '', None, None
        logger.info('connected with role {} to ok'.format(self.role))
        return (
            Sender(self._chan, send_exchange_name, send_routing_key, reply_to=reply_to),
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

Message = namedtuple('Message', 'body,reply_to,correlation_id')


class Sender:

    def __init__(self, channel, exchange_name=None, routing_key=None, reply_to=None):
        self._chan = channel
        self._exchange_name = exchange_name
        self._routing_key = routing_key
        self._reply_to = reply_to

    async def send(self, message, routing_key=None, correlation_id=None):
        if routing_key is None:
            routing_key = self._routing_key
        properties = {}
        if correlation_id is not None:
            properties['correlation_id'] = correlation_id
        if self._reply_to is not None:
            properties['reply_to'] = self._reply_to
        await self._chan.basic_publish(
            message,
            exchange_name=self._exchange_name,
            routing_key=routing_key,
            properties=properties
        )
        logger.debug('publishing message %r to exchange %r with routing key %r', message, self._exchange_name,
                     routing_key)


class Receiver:

    def __init__(self, channel, queue_name):
        self._channel = channel
        self._queue_name = queue_name
        self._fifo = asyncio.Queue(100)

    async def __call__(self, channel, body, envelope, properties):
        logger.debug('received message %r with envelope %r and properties %r', body, envelope, properties)
        try:
            # TODO: get encoding
            self._fifo.put_nowait(Message(body.decode(), properties.reply_to, properties.correlation_id))
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
