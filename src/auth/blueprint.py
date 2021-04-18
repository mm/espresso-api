"""Blueprint for auth routes (checking current user, syncing between local
and Firebase stores, and API key generation)
"""

from flask import Blueprint, jsonify, g

from src.exceptions import AuthError
from src.model import User, UserSchema, db

from .decorators import require_jwt, requires_auth
from .service import AuthService, current_uid, current_user


auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/user", methods=["GET"])
@requires_auth(allowed=["jwt", "api-key"])
def get_user():
    """Returns information about the user to display on the UI."""
    user = current_user()
    user_details = UserSchema().dump(user)
    return jsonify(**user_details, links=len(user.links)), 200


@auth_bp.route("/user_hook", methods=["POST"])
@require_jwt
def associate_new_user():
    """Receives an incoming hook when a user registers using Firebase. This
    request *must* arrive with the user's JWT. It'll create an associated
    record for them in our database, where their hashed API key will eventually
    be stored.
    """
    uid = current_uid()
    if not uid:
        raise AuthError("This method requires authorization")

    user_id = AuthService.associate_external_user(uid=uid)
    if user_id:
        return jsonify(message="User synced in local store", id=user_id), 200
    return jsonify(message="User already exists"), 400


# TODO: Add additional protection on this endpoint, for testing purposes right now
@auth_bp.route("/create_api_key", methods=["POST"])
@requires_auth(allowed=["jwt"])
def create_api_key():
    """Creates an API key for the given user. Any existing
    API key is overwritten.
    """
    uid = current_uid()
    if not uid:
        raise AuthError("This method requires authorization")
    user = User.user_at_uid(uid)
    api_key_pair = AuthService.generate_api_key()
    user.api_key = api_key_pair.hashed_key
    db.session.commit()
    return jsonify(message="API token generated", api_key=api_key_pair.api_key), 200
