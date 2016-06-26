import logging

import click
import aiohttp.web


@click.command()
def serve():
    from .. import config
    logging.basicConfig(level=logging.DEBUG)
    host, port = config.get_host_port()
    aiohttp.web.main(['-H', host, '-P', port, 'pushpull.websocket.server:serve'])


if __name__ == '__main__':
    serve()
