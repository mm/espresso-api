"""Contains methods for generating API keys and validating
whether an API key matches the hash stored on record for a user.
"""

from functools import wraps
from typing import NamedTuple
from secrets import token_hex, compare_digest
from hashlib import sha256
import os
import requests
from flask import request, jsonify, current_app
from jose import jwt
from src.model import User

api_pair = NamedTuple('KeyDetails', [('api_key', str), ('hashed_key', str)])

class AuthError(Exception):
    """Exception raised when validating incoming JWTs or API
    keys.
    """
    def __init__(self, message, status_code=401):
        self.message = message
        self.status_code = status_code


class AuthService:
    """Service used to interact with Auth0, generate or validate
    API keys for a given user.
    """

    def __init__(self):
        self.auth0_domain = os.getenv('AUTH0_DOMAIN')
        self.auth0_audience = os.getenv('AUTH0_API_AUDIENCE')
    
        if (not self.auth0_domain) or (not self.auth0_audience):
            current_app.logger.error("Auth0 domain and audience missing")
            raise AuthError("Authentication service not available")

    
    def _get_auth_token_header(self, bearer_token: str) -> str:
        """From a token like `Bearer _______`, pulls out the _____
        part to extract the token itself (and check if we're in the
        right format to begin with)
        """
        parts = bearer_token.split()

        if (parts[0].lower() != "bearer") or (len(parts) == 1) or (len(parts) > 2):
            raise AuthError("Authorization token given in the incorrect format")
    
        return parts[1]


    def _validate_jwt(self, token: str) -> User:
        """Validates a JWT against the JSON Web Key Set hosted
        on Auth0.
        """
        
        jwks = None
        try:
            jwks = requests.get(
                f'https://{self.auth0_domain}/.well-known/jwks.json'
            ).json()
        except Exception as e:
            current_app.logger.error(f"Could not fetch JWKS: {e}")
            raise AuthError("Could not validate against JSON Web Key Set")
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=['RS256'],
                    audience=self.auth0_audience,
                    issuer=f'https://{self.auth0_domain}/'
                )
            except jwt.ExpiredSignatureError:
                raise AuthError("Authorization token expired")
            except jwt.JWTClaimsError:
                raise AuthError("Incorrect claims")
            except Exception:
                raise AuthError("Authorization failed")
            print(payload)
        else:
            raise AuthError("Unable to find required key")


def generate_api_key() -> api_pair:
    """Generates a random token to use as an API key.
    Returns a named tuple containing the key (`api_key`) and a hash
    value (`hashed_key`). The hashed version is what is saved
    to the database.
    """

    api_key = str(token_hex(32))  # 32 bytes of randomness
    hash_value = sha256(api_key.encode('utf-8')).hexdigest()
    return api_pair(api_key, hash_value)


def validate_api_key(user_id: int, api_key: str) -> bool:
    """Checks the hash of the API key submitted against
    that currently stored in the database. Returns True
    if the key is a match.

    Arguments:
    - user_id: An integer representing the user in the database
    - api_key: The key to check against
    """
    if (not user_id) or (not api_key):
        return False

    # Compute SHA-256 hash of API key to check:
    submitted_hash = sha256(api_key.encode('utf-8')).hexdigest()

    # Get hash for user ID in database:
    try:
        user = User.query.get(user_id)
        user_hash = user.api_key
    except Exception as e:
        print("User fetching failed.")
        return False
    
    return compare_digest(submitted_hash, user_hash)


def user_for_api_key(api_key: str) -> User:
    """Returns a User object for a specified API key,
    or None if no user exists with that key.
    """
    
    if api_key:
        # Compute SHA-256 hash of API key to query table for:
        key_hash = sha256(api_key.encode('utf-8')).hexdigest()

        # Check table for a User with that key:
        user = User.query.filter_by(api_key=key_hash).first()
        return user
    return None



def user_from_jwt(authorization_header):
    """Attempts to validate a JWT and retrieve the user from the JWT
    claims. Returns a User object if authentication was successful.
    """
    auth = AuthService()
    token = auth._get_auth_token_header(authorization_header)
    auth._validate_jwt(token)


def requires_auth(f):
    """Wraps a view function to ensure a valid JWT or
    API key has been provided in the request. 
    
    Will yield a 403 if unsuccessful, or return the view function 
    with the `current_user` variable populated as a User object otherwise.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = None
        if 'Authorization' in request.headers:
            # JWT may have been passed in, validate it:
            user = user_from_jwt(request.headers.get('Authorization'))
        if 'x-api-key' in request.headers:
            # User may have passed an API key:
            api_key = request.headers.get('x-api-key')
            user = user_for_api_key(api_key)
        if user is None:
            raise AuthError("Authorization is required to access this resource")
        return f(*args, **kwargs, current_user=user)
    return decorated_function
