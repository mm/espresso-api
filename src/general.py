"""Blueprint for general helper endpoints.
"""

from flask import Blueprint, jsonify

general_bp = Blueprint("general_bp", __name__)


@general_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify(message="API is online"), 200
