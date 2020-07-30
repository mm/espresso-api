"""Contains methods for generating API keys and validating
whether an API key matches the hash stored on record for a user.
"""

from functools import wraps
from typing import NamedTuple
from uuid import uuid4
from hashlib import sha256
from flask import request, jsonify
from untitled.model import User

api_pair = NamedTuple('KeyDetails', [('api_key', str), ('hashed_key', str)])


def generate_api_key() -> api_pair:
    """Generates a random UUID to use as an API key.
    Returns a named tuple containing the key (`api_key`) and a hash
    value (`hashed_key`). The hashed version is what is saved
    to the database.
    """

    api_key = str(uuid4())
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

    # Compute SHA-256 hash of API key to check:
    submitted_hash = sha256(api_key.encode('utf-8')).hexdigest()

    # Get hash for user ID in database:
    try:
        user = User.query.filter_by(id=user_id).first()
        user_hash = user.api_key
    except Exception as e:
        print("User fetching failed.")
        return False
    
    return user_hash == submitted_hash


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


def api_key_auth(f):
    """Wraps a view function to check the `x-api-key` header against
    an API key stored in the database. Will yield a 403 if unsuccessful,
    or return the view function with the `current_user` variable populated
    as a User object otherwise.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        user = user_for_api_key(api_key)
        if user is None:
            return jsonify(error="Invalid API key"), 403
        return f(*args, **kwargs, current_user=user)
    return decorated_function
