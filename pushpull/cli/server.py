import logging

import click
import aiohttp.web


@click.command()
def serve():
    logging.basicConfig(level=logging.DEBUG)
    aiohttp.web.main(['-H', 'localhost', '-P', '8080', 'pushpull.websocket.server:serve'])


if __name__ == '__main__':
    serve()
