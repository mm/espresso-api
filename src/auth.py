"""Contains methods for generating API keys and validating
whether an API key matches the hash stored on record for a user.
"""

from functools import wraps
from re import split
from typing import NamedTuple
from secrets import token_hex, compare_digest
from hashlib import sha256
import os
import requests
from flask import request, jsonify, current_app
from sqlalchemy import or_
from src.model import User
from src.firebase import FirebaseService, FirebaseServiceError

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
        self.firebase = FirebaseService()

    
    def _split_bearer_token(self, header_token:str) -> str:
        """Parses a Bearer token into its parts (so all we have
        to verify is a JWT). Returns the JWT, or complains about
        the token not being in Bearer ____ format.
        """
        token = None
        split_header = header_token.split(' ')
        if (len(split_header) == 2) and (split_header[0].lower() == 'bearer') and (split_header[1]):
            return split_header[1].strip()
        raise AuthError("Tokens provided in the incorrect format")


    def _uid_from_token(self, id_token:str) -> str:
        """Validates a token to return a Firebase UID.
        """
        print(f"Incoming: {id_token}")
        try:
            uid = self.firebase.verify_id_token(id_token)
            if not uid:
                raise AuthError("Could not find a user using that token")
            return uid
        except FirebaseServiceError as fe:
            raise AuthError(message=fe.message)
        except Exception as e:
            current_app.logger.error(f"Unhandled user_for_uid error: {e}")
            raise


    def user_for_token(self, id_token:str) -> User:
        """Returns a User instance, given an ID token from Firebase.
        The token is first validated to return a Firebase UID. Then,
        the UID is looked up in the database to yield a User object.
        """
        uid = self._uid_from_token(id_token)
        user = User.query.filter_by(external_uid=uid).first()
        return user

    
    def associate_external_user(self, uid:str) -> User:
        """Creates a User object with identifying information from Firebase
        (UID). When a user registers, this will eventually get called,
        which will give the user a record in the database. Later, they can create
        an API key (which also saves to the database)
        """

        user_info = self.firebase.user_info_at_uid(uid)

        # First, check: does a user already exist with this email or Firebase UID?
        user = User.query.filter(or_(User.email == user_info['email'], User.external_uid == uid)).first()
        if user:
            return user
        # Okay, good to create a new User:
        user_id = User.create(name=user_info['name'], firebase_uid=uid, email=user_info['email'])
        return User.query.get(user_id)


auth = AuthService()

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
            bearer_token = auth._split_bearer_token(request.headers.get('Authorization'))
            user = auth.user_for_token(bearer_token)
        if 'x-api-key' in request.headers:
            # User may have passed an API key:
            api_key = request.headers.get('x-api-key')
            user = user_for_api_key(api_key)
        if user is None:
            raise AuthError("Authorization is required to access this resource")
        return f(*args, **kwargs, current_user=user)
    return decorated_function


def require_jwt(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        uid = None
        if 'Authorization' in request.headers:
            # JWT may have been passed in, validate it:
            bearer_token = auth._split_bearer_token(request.headers.get('Authorization'))
            uid = auth._uid_from_token(bearer_token)
        if uid is None:
            raise AuthError("Authorization is required to access this resource")
        return f(*args, **kwargs, uid=uid)
    return decorated_function