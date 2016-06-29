import django
from oauth2_provider.models import AccessToken


def main():
    django.setup()
    return authenticate


async def authenticate(token):
    try:
        access_token = AccessToken.objects.select_related('user').get(token=token)
    except AccessToken.DoesNotExist:
        return None
    if access_token.is_valid():
        return access_token.user.pk, access_token.user.get_username()
    return None
