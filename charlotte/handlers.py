"""Contains exception handlers to be registered on the API blueprint.
"""

from flask import jsonify, current_app

def handle_invalid_data(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def handle_not_found(error):
    return jsonify(message="Requested resource was not found in the database"), 404

def handle_server_error(error):
    return jsonify(message="An unknown error while accessing resource"), 500

def handle_sqa_general(error):
    """Catch-all for any SQLAlchemy error we haven't caught explicitly already"""
    current_app.logger.error(f"Database error: {error}")
    return jsonify(message="An error occured while communicating with the database"), 500

def handle_validation_error(error):
    """Catches exceptions related to data validation in Marshmallow"""
    return jsonify(message="The submitted data failed validation checks", issues=error.messages), 422