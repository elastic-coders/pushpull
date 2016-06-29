import functools


def main(filename):
    with open(filename, 'r') as db:
        tokens = {
            line.split(':')[-1].rstrip(): line.split(':')[:-1] for line in db.readlines()
        }
    return functools.partial(authenticator, tokens)


async def authenticator(tokens, token):
    return tokens.get(token)
