"""Contains exception handlers to be registered on the API blueprint.
"""

from flask import jsonify, current_app

def handle_invalid_data(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def handle_not_found(error):
    return jsonify(error="Requested resource was not found in the database"), 404

def handle_server_error(error):
    return jsonify(error="An unknown error while accessing resource"), 500

def handle_sqa_general(error):
    """Catch-all for any SQLAlchemy error we haven't caught explicitly already"""
    current_app.logger.error(f"Database error: {error}")
    return jsonify(error="An error occured while communicating with the database"), 500

def handle_validation_error(error):
    """Catches exceptions related to data validation in Marshmallow"""
    return jsonify(error="The submitted data failed validation checks", issues=error.messages), 422