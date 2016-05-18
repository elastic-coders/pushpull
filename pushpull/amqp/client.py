import logging

from .gateway import Exchanger
from ..linereader import FdLineReader

logger = logging.getLogger(__name__)


async def challenge(fd):
    async with Exchanger('1') as (sender, _):
        async for line in FdLineReader(fd):
            logger.debug('sending message %r', line)
            await sender.send(line)
