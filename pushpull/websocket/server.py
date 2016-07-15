import aiohttp.web
import aiohttp_cors

from . import gateway
from .. import config


def serve(argv):
    app = aiohttp.web.Application()
    cors = aiohttp_cors.setup(app)
    resource = cors.add(app.router.add_resource(config.get_url_path()))
    route = resource.add_route('GET', gateway.websocket_rabbitmq_gateway)
    cors.add(
        route,
        {
            origin: aiohttp_cors.ResourceOptions(
                allow_credentials=True,
            )
            for origin in config.get_cors_allowed_origins()
        }
    )
    return app
