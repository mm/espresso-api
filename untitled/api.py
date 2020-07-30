"""Blueprint containing API routes for Untitled. All
routes will be prefixed with /api.
"""

from flask import Blueprint
from untitled.model import db
from untitled.auth import api_key_auth

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/')
@api_key_auth
def index(current_user=None):
    pass