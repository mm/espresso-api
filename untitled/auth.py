"""Contains methods for generating API keys and validating
whether an API key matches the hash stored on record for a user.
"""

from typing import NamedTuple
from uuid import uuid4
from hashlib import sha256
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