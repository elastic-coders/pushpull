class RPCBase:

    ROLE_WS = 1
    ROLE_APP = 2

    def __init__(self, role, client_id=0, url=None):
        if role not in [self.ROLE_WS, self.ROLE_APP]:
            raise ValueError('bad role {}'.format(role))
        self.role = role
        self.client_id = client_id
        self.url = url

    def get_app_exchange_name(self):
        return 'pushpull.rpc'

    def get_app_routing_key(self):
        return 'pushpull.rpc'
