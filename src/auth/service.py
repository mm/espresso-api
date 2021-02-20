"""Classes and functions to handle token/API key validation using the
Firebase Auth store or local store.
"""

from typing import NamedTuple, Union
from secrets import token_hex, compare_digest
from hashlib import sha256
from flask import current_app, g
from sqlalchemy import or_
from src.model import User, db, Link
from src.exceptions import FirebaseServiceError, AuthError
from .firebase import firebase_service


firebase = firebase_service


class AuthService:
    """Service used to authenticate users on the platform, via JWT or
    API key. Interfaces with Firebase to validate JWTs and interfaces
    with the local database to validate API keys.
    """

    api_pair = NamedTuple('KeyDetails', [('api_key', str), ('hashed_key', str)])


    @classmethod
    def _split_bearer_token(cls, header_token:str) -> str:
        """Parses a Bearer token into its parts (so all we have
        to verify is a JWT). Returns the JWT, or complains about
        the token not being in Bearer ____ format.
        """
        token = None
        split_header = header_token.split(' ')
        if (len(split_header) == 2) and (split_header[0].lower() == 'bearer') and (split_header[1]):
            return split_header[1].strip()
        raise AuthError("Tokens provided in the incorrect format")


    @classmethod
    def _uid_from_token(cls, id_token:str) -> str:
        """Validates a token to return a Firebase UID.
        """
        try:
            uid = firebase.verify_id_token(id_token)
            if not uid:
                raise AuthError("Could not find a user using that token")
            return uid
        except FirebaseServiceError as fe:
            raise AuthError(message=fe.message)
        except Exception as e:
            current_app.logger.error(f"Unhandled user_for_uid error: {e}")
            raise

    
    @classmethod
    def token_to_uid(cls, auth_header:str) -> str:
        """Wraps the _uid_from_token and _split_bearer_token methods,
        returning a Firebase UID if the token was valid.
        """
        bearer_token = cls._split_bearer_token(auth_header)
        uid = cls._uid_from_token(bearer_token)
        return uid


    @classmethod
    def associate_external_user(cls, uid:str) -> Union[int, None]:
        """Creates a User object with identifying information from Firebase
        (UID). When a user registers, this will eventually get called,
        which will give the user a record in the database. Later, they can create
        an API key (which also saves to the database)
        """

        user_info = firebase.user_info_at_uid(uid)
        user_id = None
        # First, check: does a user already exist with this email or Firebase UID?
        user = User.query.filter(or_(User.email == user_info['email'], User.external_uid == uid)).first()
        if not user:
            user_id = User.create(name=user_info['name'], firebase_uid=uid, email=user_info['email'])
        else:
            if not user.external_uid:
                # User exists with an email that matches the one on Firebase, but no UID:
                user.external_uid = uid
                db.session.commit()
                user_id = user.id
        return user_id


    @classmethod
    def generate_api_key(cls) -> api_pair:
        """Generates a random token to use as an API key.
        Returns a named tuple containing the key (`api_key`) and a hash
        value (`hashed_key`). The hashed version is what is saved
        to the database.
        """

        api_key = str(token_hex(32))  # 32 bytes of randomness
        hash_value = sha256(api_key.encode('utf-8')).hexdigest()
        return cls.api_pair(api_key, hash_value)


    @classmethod
    def validate_api_key(cls, user_id: int, api_key: str) -> bool:
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


    @classmethod
    def user_for_api_key(cls, api_key: str) -> User:
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
        
    
    @classmethod
    def check_link_access(cls, user_id: int, link: Link) -> Union[None, bool]:
        """Simple check to make sure a link's user ID is equal
        to the user ID accessing the link. Will raise an AuthError
        if the check fails.
        """
        if user_id != link.user_id:
            raise AuthError(
                message="You are not authorized to access this item",
                status_code=403
            )
        return True

    
    @classmethod
    def user_for_token(cls, id_token:str) -> User:
        """Returns a User instance, given an ID token from Firebase.
        The token is first validated to return a Firebase UID. Then,
        the UID is looked up in the database to return a User object.
        """
        uid = cls._uid_from_token(id_token)
        user = User.query.filter_by(external_uid=uid).first()
        return user


def current_user() -> User:
    """Returns the current user from the Flask application global,
    or raises an AuthError if one can't be found.
    """
    if 'current_user' not in g:
        raise AuthError('This method requires authorization')
    return g.current_user


def current_uid() -> Union[str, None]:
    """Returns the current Firebase UID from the Flask application
    global, useful in endpoints where a User might not exist yet.
    """
    if 'current_uid' in g:
        return g.current_uid