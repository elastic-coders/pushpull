import aiohttp.web

from . import gateway


def serve(argv):
    app = aiohttp.web.Application()
    app.router.add_route('*', '/sock', gateway.websocket_rabbitmq_gateway)
    return app
