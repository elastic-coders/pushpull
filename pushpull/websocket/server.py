import aiohttp.web

from . import gateway
from .. import config


def serve(argv):
    app = aiohttp.web.Application()
    app.router.add_route('GET', config.get_url_path(), gateway.websocket_rabbitmq_gateway)
    return app
