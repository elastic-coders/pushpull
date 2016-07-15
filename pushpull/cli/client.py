import asyncio
import sys
import logging
import importlib
import re

import click


@click.group()
def client():
    pass


@click.command()
@click.argument('url')
@click.argument('token')
def challenge_websocket(url, token):
    from ..websocket import client as websocket_client
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    click.echo(loop.run_until_complete(websocket_client.challenge(url, token, sys.stdin, sys.stdout, loop)))
client.add_command(challenge_websocket)


@click.command()
@click.argument('url')
@click.argument('user_id')
def challenge_amqp(url, user_id):
    from ..amqp import client as amqp_client
    logging.basicConfig(level=logging.DEBUG)
    click.echo(asyncio.get_event_loop().run_until_complete(amqp_client.challenge(url, user_id, sys.stdin, sys.stdout)))
client.add_command(challenge_amqp)


@click.command()
@click.argument('url')
@click.argument('authenticator')
def authenticate_amqp(url, authenticator):
    from ..amqp import client as amqp_client
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    mo = re.match(r'(?P<module>.+):(?P<function>\w[_\w]*)(?:,(?P<params>.+))?', authenticator)
    if not mo:
        raise click.BadParameter('bad authenticator', param_hint='authenticator')
    module, funct, params = mo.groups()
    params = params.split(',') if params else []
    try:
        authenticator_factory = getattr(importlib.import_module(module), funct)
    except ImportError as exc:
        raise click.BadParameter('authenticator module %s not found' % module, param_hint='authenticator') from exc
    except AttributeError:
        raise click.BadParameter('authenticator module %s does not have function %s ' % (module, funct),
                                 param_hint='authenticator')
    logger.info('using authenticator module %s function %s with params %r' % (module, funct, params))
    authenticator = authenticator_factory(*params)
    click.echo(asyncio.get_event_loop().run_until_complete(amqp_client.authenticate(url, authenticator)))
client.add_command(authenticate_amqp)


if __name__ == '__main__':
    client()
