from django.contrib.auth import authenticate

from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError


def login_service(username, password):

    user = authenticate(
        username=username,
        password=password,
    )

    if user is None:
        raise AuthenticationFailed("Invalid username or password.")

    refresh = RefreshToken.for_user(user)

        #چون View بعداً می‌خواهد اطلاعات User را Serialize کند
        # پس اطلاعات را ریترن میکند
    return {
        "user": user,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }

def logout_service(refresh_token):

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()

    except Exception:
        raise ValidationError("Invalid refresh token.")