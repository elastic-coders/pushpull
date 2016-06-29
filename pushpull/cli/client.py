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
@click.argument('token')
def challenge_websocket(url, token):
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    click.echo(loop.run_until_complete(websocket_client.challenge(url, token, sys.stdin, sys.stdout, loop)))
client.add_command(challenge_websocket)


@click.command()
@click.argument('url')
@click.argument('user_id')
def challenge_amqp(url, user_id):
    logging.basicConfig(level=logging.DEBUG)
    click.echo(asyncio.get_event_loop().run_until_complete(amqp_client.challenge(url, user_id, sys.stdin, sys.stdout)))
client.add_command(challenge_amqp)


@click.command()
@click.argument('url')
@click.argument('db', type=click.File('r'))
def authenticate_amqp(url, db):
    logging.basicConfig(level=logging.DEBUG)
    tokens = {
        line.split(':')[-1].rstrip(): line.split(':')[:-1] for line in db.readlines()
    }
    click.echo(asyncio.get_event_loop().run_until_complete(amqp_client.authenticate(url, tokens)))
client.add_command(authenticate_amqp)


if __name__ == '__main__':
    client()
