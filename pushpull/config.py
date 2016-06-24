import urllib.parse
import os

try:
    from django.conf import settings
except ImportError:
    WEBSOCKET_URL = os.environ.get('PUSHPULL_WEBSOCKET_URL', '')
    BROKER_URL = os.environ.get('PUSHPULL_BROKER_URL', '')
else:
    WEBSOCKET_URL = settings.PUSHPULL_WEBSOCKET_URL
    BROKER_URL = settings.PUSHPULL_BROKER_URL


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


def get_amqp_conn_params():
    url = BROKER_URL or 'amqp://guest:guest@localhost:5672/'
    url_chunks = urllib.parse.urlparse(url)
    if '@' not in url_chunks.netloc:
        host_port = url_chunks.netloc
        username, password = None, None
    else:
        auth, host_port = url_chunks.netloc.split('@')
        if ':' in auth:
            username, password = auth.split(':')
        else:
            username, password = None, None
    if not username:
        username = 'guest'
    if not password:
        password = 'guest'
    if ':' in host_port:
        host, port = host_port.split(':')
    else:
        host = host_port
        port = None
    if not port:
        port = 5672
    else:
        port = int(port)
    path = url_chunks.path
    if not path:
        path = '/'
    return {
        'host': host,
        'port': port,
        'username': username,
        'password': password,
        'virtual_host': path,
    }
