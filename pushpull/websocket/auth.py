def encode_auth_querystring_param(token):
    return {'http-authorization': token}


def decode_auth_querystring_param(params):
    return params.get('http-authorization')
