"""Blueprint for helper endpoints.
"""

from flask import Blueprint, jsonify
from src.model import UserSchema
from src.auth.service import current_user
from src.auth.decorators import requires_auth
from src.exceptions import AuthError
import src.handlers as handlers

api_bp = Blueprint('api_bp', __name__)

#  Exception handlers:
api_bp.register_error_handler(AuthError, handlers.handle_auth_error)


@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify(message='API is online'), 200


#  /user routes:
@api_bp.route('/user', methods=['GET'])
@requires_auth(allowed=['jwt', 'api-key'])
def user():
    """Returns information about the user to display on the UI.
    """
    user = current_user()
    user_details = UserSchema().dump(user)
    return jsonify(
        **user_details,
        links=len(user.links)
    ), 200
