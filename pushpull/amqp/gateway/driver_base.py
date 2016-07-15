class ExchangerBase:

    ROLE_WS = 1
    ROLE_APP = 2

    def __init__(self, name, role, client_id=0, url=None):
        if role not in [self.ROLE_WS, self.ROLE_APP]:
            raise ValueError('bad role {}'.format(role))
        self.role = role
        self.client_id = client_id
        self.name = name
        self.url = url

    def get_app_exchange_name(self):
        return 'pushpull.app'

    def get_app_routing_key(self):
        return ''

    def get_ws_exchange_name(self):
        return 'pushpull.ws'

    def get_ws_routing_key(self, broadcast=False):
        if broadcast:
            return 'pushpull.ws'
        return 'pushpull.ws.{}'.format(self.name)
