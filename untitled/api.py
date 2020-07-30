"""Blueprint containing API routes for Untitled. All
routes will be prefixed with /api.
"""

from flask import Blueprint, jsonify, request
from untitled.model import db
from untitled.auth import api_key_auth

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/user', methods=['GET'])
@api_key_auth
def user(current_user=None):
    """Returns information about the user (authenticated via
    API key).
    """
    if current_user:
        return jsonify(
            user_id=current_user.id,
            name=current_user.name,
            links=len(current_user.links)
        ), 200
    else:
        return jsonify(error="Unknown error while describing user"), 500


@api_bp.route('/links', methods=['GET', 'POST'])
@api_key_auth
def links(current_user=None):
    """Returns a list of links for the current user (and pointers
    to another page of links), or allows for the creation of new
    links (data received in JSON payload)
    """
    if request.method == 'GET':
        # Fetch all links, applying pagination as necessary
        # Check 'page' URL parameter to get what page we're on and
        # adjust result set as necessary
        # TODO: Don't just fetch the whole set, paginate
        results = [link.to_dict() for link in current_user.links]
        return jsonify(
            number_of_links=len(current_user.links),
            page=1,
            total_pages=1,
            next_page=1,
            links=results
        )
    # Otherwise, we're creating a new link
    # TODO: Implement POST
    # 1) Collect information via the JSON body of the request
    # 2) Validate info
    # 3) If title isn't specified, attempt to scrape the site to get it
    # 4) Ultimately add to database and return ID


@api_bp.route('/links/<int:id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@api_key_auth
def link(id, current_user=None):
    """Methods for fetching, updating or deleting a link.
    """
    return f'Received {id}'