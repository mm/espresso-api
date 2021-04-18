"""Stores auth-related decorators to use across any
route that requires authentication.
"""

from flask import request, g
from functools import wraps
from src.exceptions import AuthError
from .service import AuthService


def requires_auth(allowed=["api-key", "jwt"]):
    """Wraps a view function to ensure a valid JWT or
    API key has been provided in the request. By default both methods
    are allowed.

    Will yield a 403 if unsuccessful, or return the view function
    with the application global current_user populated otherwise.
    """

    def auth_decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = None
            if ("jwt" in allowed) and ("Authorization" in request.headers):
                # JWT may have been passed in, validate it:
                bearer_token = AuthService._split_bearer_token(
                    request.headers.get("Authorization")
                )
                user = AuthService.user_for_token(bearer_token)
            if ("api-key" in allowed) and ("x-api-key" in request.headers):
                # User may have passed an API key:
                api_key = request.headers.get("x-api-key")
                user = AuthService.user_for_api_key(api_key)
            if user is None:
                raise AuthError("Authorization is required to access this resource")
            else:
                g.current_user = user
            return f(*args, **kwargs)

        return decorated_function

    return auth_decorator


def require_jwt(f):
    """Wraps a view function that requires a valid JWT to proceed.
    For example, endpoints that generate or rotate API keys would
    use this decorator, or ones that sync new Firebase users to the local
    data store. Will populate the current_uid global instead of current_user
    since a User object might not exist in the local datastore yet.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        uid = None
        if "Authorization" in request.headers:
            # JWT may have been passed in, validate it:
            uid = AuthService.token_to_uid(request.headers.get("Authorization"))
        if uid is None:
            raise AuthError("Authorization is required to access this resource")
        g.current_uid = uid
        return f(*args, **kwargs)

    return decorated_function
