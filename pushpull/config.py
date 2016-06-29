import urllib.parse
import os

# TODO: more modular settings
WEBSOCKET_URL = os.environ.get('PUSHPULL_WEBSOCKET_URL', '')
BROKER_URL = os.environ.get('PUSHPULL_BROKER_URL', '')
CORS_ALLOWED_ORIGINS = os.environ.get('PUSHPULL_CORS_ALLOWED_ORIGINS', '')


def get_host_port():
    url = WEBSOCKET_URL or 'http://localhost:8080'
    url_chunks = urllib.parse.urlparse(url)
    host_port = url_chunks.netloc
    if ':' in host_port:
        host, port = host_port.split(':')
    else:
        host = host_port
        port = '8080'
    return host, port


def get_url_path():
    path = '/pushpull'
    if WEBSOCKET_URL:
        url_chunks = urllib.parse.urlparse(WEBSOCKET_URL)
        path = url_chunks.path
    return path


def get_amqp_conn_params(url=None):
    if url is None:
        url = BROKER_URL or 'amqp://guest:guest@localhost:5672/'
    url = urllib.parse.urlparse(url)
    return {
        'host': url.hostname or 'localhost',
        'port': url.port,
        'username': url.username or 'guest',
        'password': url.password or 'guest',
        'virtual_host': url.path[1:] if len(url.path) > 1 else '/',
        'ssl': url.scheme == 'amqps'
    }


def get_cors_allowed_origins():
    if CORS_ALLOWED_ORIGINS:
        return CORS_ALLOWED_ORIGINS.split(',')
    return []


def get_cors_allow_credentials():
    return True


def get_ws_autoping_timeout():
    return 15
