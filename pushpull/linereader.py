import asyncio
import logging

logger = logging.getLogger(__name__)


class FdLineReader:

    def __init__(self, fd, loop=None):
        self._fd = fd
        self._queue = asyncio.Queue()
        self._loop = loop or asyncio.get_event_loop()
        self._loop.run_in_executor(None, self._read_fd)

    async def __aiter__(self):
        return self

    async def __anext__(self):
        data = await self._queue.get()
        if data is None:
            raise StopAsyncIteration
        return data

    def _read_fd(self):
        logging.debug('start reading from fd')
        for line in self._fd:
            logging.debug('read line: %r', line)
            asyncio.run_coroutine_threadsafe(self._queue.put(line.rstrip()), self._loop)
        logging.debug('end reading from fd')
        asyncio.run_coroutine_threadsafe(self._queue.put(None), self._loop)
