"""Blueprint containing API routes for Untitled. All
routes will be prefixed with /api.
"""

from flask import Blueprint, jsonify, request
from untitled.model import db, Link
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
        
        # Default to page 1, with 20 URLs per page:
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
        except ValueError:
            return jsonify(error="If provided, page and per_page must be integers"), 400

        try:
            link_query = Link.query.filter(Link.user_id==current_user.id).order_by(Link.date_added).paginate(
                page=page, per_page=per_page
            )
            # Here, `items` is the Link objects for the current page:
            results = [link.to_dict() for link in link_query.items]
            return jsonify(
                total_links=len(current_user.links),
                page=link_query.page,
                total_pages=link_query.pages,
                next_page=link_query.next_num,
                per_page=per_page,
                links=results
            )
        except Exception as e:
            # TODO: Way better error handling here (i.e. dealing w/ pagination inputs)
            print(f'Error fetching links: {e}')
            return jsonify(error="Error fetching links"), 500

    # Otherwise, we're creating a new link
    # TODO: Implement POST
    # Collect information via the JSON body of the request
    body = request.get_json()
    # At minimum, the body needs to have a `url` key. Without it, we can't even
    # infer the title. So we check for this outright:
    if body and ('url' in [*body]):
        # 2) Validate info
        # 3) If title isn't specified, attempt to scrape the site to get it
        # 4) Ultimately add to database and return ID
        return 'POST received'
    else:
        # JSON was invalid
        return jsonify(error="Must POST valid JSON data"), 400


@api_bp.route('/links/<int:id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@api_key_auth
def link(id, current_user=None):
    """Methods for fetching, updating or deleting a link.
    """
    return f'Received {id}'