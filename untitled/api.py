"""Blueprint containing API routes for Untitled. All
routes will be prefixed with /api.
"""

from flask import Blueprint
from untitled.model import db

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/')
def index():
    print(db)
    return 'hello'