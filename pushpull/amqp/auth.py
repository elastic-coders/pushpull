import json
import uuid
from collections import namedtuple
import asyncio

from .rpc.driver_aioamqp import RPC

User = namedtuple('User', 'id,username')


async def get_user_info(authorization, client_id=None):
    async with RPC(RPC.ROLE_WS, client_id=client_id) as (amqp_sender, amqp_receiver):
        correlation_id = await send_user_info_request(amqp_sender, authorization)
        try:
            reply = await asyncio.wait_for(receive_user_info_response(amqp_receiver, correlation_id), 5)
        except asyncio.TimeoutError as exc:
            raise AuthTimeout from exc
        if reply is None:
            raise NotAuthorized()
        return reply


async def send_user_info_request(sender, authorization):
    correlation_id = str(uuid.uuid4())
    await sender.send(encode_authorization_request(authorization), correlation_id=correlation_id)
    return correlation_id


async def receive_user_info_response(receiver, correlation_id):
    async for message in receiver:
        if message.correlation_id != correlation_id:
            pass
        return decode_authorization_reply(message.body)


def encode_authorization_request(authorization):
    return json.dumps({'authorization': authorization})


def decode_authorization_request(payload):
    return json.loads(payload)['authorization']


def encode_authorization_error_reply():
    return json.dumps(None)


def encode_authorization_reply(user_id, username):
    return json.dumps({'id': user_id, 'username': username})


def decode_authorization_reply(body):
    data = json.loads(body)
    if data is None:
        return None
    return User(data['id'], data['username'])


class AuthorizationError(Exception):
    pass


class NotAllowed(AuthorizationError):
    pass


class NotAuthorized(AuthorizationError):
    pass


class AuthTimeout(AuthorizationError):
    pass
