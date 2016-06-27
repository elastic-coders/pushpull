import asyncio
import sys
import logging

import click

from ..websocket import client as websocket_client
from ..amqp import client as amqp_client


@click.group()
def client():
    pass


@click.command()
@click.argument('url')
@click.argument('name')
def challenge_websocket(url, name):
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    click.echo(loop.run_until_complete(websocket_client.challenge(url, name, sys.stdin, sys.stdout, loop)))
client.add_command(challenge_websocket)


@click.command()
@click.argument('url')
@click.argument('name')
def challenge_amqp(url, name):
    logging.basicConfig(level=logging.DEBUG)
    click.echo(asyncio.get_event_loop().run_until_complete(amqp_client.challenge(url, name, sys.stdin, sys.stdout)))
client.add_command(challenge_amqp)


if __name__ == '__main__':
    client()
