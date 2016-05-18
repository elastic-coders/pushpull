import logging
import asyncio

import asynqp


logger = logging.getLogger(__name__)


class Exchanger:

    def __init__(self, name, **connection_params):
        self.exchange_name = name
        self._conn_params = connection_params

    async def __aenter__(self):
        logger.debug('connecting sender and receiver')
        self._conn = await asynqp.connect(**self._conn_params)
        self._chan = await self._conn.open_channel()
        exchange = await self._chan.declare_exchange(self.exchange_name, 'direct')
        queue = await self._chan.declare_queue(self.exchange_name)
        await queue.bind(exchange, self.exchange_name)
        logger.debug('connected sender and receiver')
        return Sender(exchange, self.exchange_name), Receiver(queue)

    async def __aexit__(self, exc_type, exc_value, traceback):
        logger.debug('closing connection and channel %r %r', exc_type, exc_value)
        try:
            await self._chan.close()
            await self._conn.close()
        except:
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
