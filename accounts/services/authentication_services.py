from django.contrib.auth import authenticate

from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken


def login_service(username, password):
    """
    Authenticate a user and generate JWT access and refresh tokens.

    Args:
        username (str): The username of the user attempting to log in.
        password (str): The password provided by the user.

    Returns:
        dict: A dictionary containing the authenticated user,
        access token, and refresh token.

    Raises:
        AuthenticationFailed: If the username or password is invalid.
    """

    user = authenticate(
        username=username,
        password=password,
    )

    if user is None:
        raise AuthenticationFailed(
            "Invalid username or password."
        )

    refresh = RefreshToken.for_user(user)

    return {
        "user": user,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def logout_service(refresh_token):
    """
    Invalidate a refresh token by adding it to the blacklist.

    Args:
        refresh_token (str): The JWT refresh token to invalidate.

    Raises:
        ValidationError: If the refresh token is invalid or cannot be
        blacklisted.
    """

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()

    except Exception:
        raise ValidationError(
            "Invalid refresh token."
        )