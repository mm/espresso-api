"""Blueprint for all endpoints that manipulate individual links.
"""

from flask import Blueprint, jsonify, request, make_response, url_for
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from src.auth.service import AuthService, current_user
from src.model import db, Link, LinkSchema
from src.auth.decorators import requires_auth
from src.exceptions import InvalidUsage, AuthError
import src.handlers as handlers


link_bp = Blueprint('link_bp', __name__)
link_schema = LinkSchema()

# Exception Handlers
link_bp.register_error_handler(404, handlers.handle_not_found)
link_bp.register_error_handler(500, handlers.handle_server_error)
link_bp.register_error_handler(InvalidUsage, handlers.handle_invalid_data)
link_bp.register_error_handler(SQLAlchemyError, handlers.handle_sqa_general)
link_bp.register_error_handler(ValidationError, handlers.handle_validation_error)
link_bp.register_error_handler(AuthError, handlers.handle_auth_error)


@link_bp.route('', methods=['GET'])
@requires_auth(allowed=['jwt', 'api-key'])
def get_links():
    """Returns a list of links for the current user (and pointers
    to another page of links) The `show` URL param controls
    whether archived links are returned, and can be one of `all`, `read`,
    or `unread` (default "unread")
    """
    user = current_user()
    # Default to page 1, with 20 URLs per page:
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
    except ValueError:
        raise InvalidUsage(message="The page and per_page parameters must be integers")

    # Check what the user wants to see based on the "show" URL param:
    # "unread": Show only unread articles (default)
    # "read": Show only read articles
    # "all": Show all articles
    show_param = request.args.get('show', 'unread')
    if show_param not in ('unread', 'read', 'all'):
        raise InvalidUsage(message="The show parameter must be either unread, read or all.")

    link_query = Link.query.filter(Link.user_id==user.id)
    # By default, the query returns all links regardless of read status. If the request
    # specifies otherwise, add this:
    if show_param == 'read':
        link_query = link_query.filter(Link.read==True)
    elif show_param == 'unread':
        link_query = link_query.filter(Link.read==False)

    # Paginate our results:
    link_query = link_query.order_by(
        Link.date_added.desc()
    ).paginate(page=page, per_page=per_page)

    # Here, `items` is the Link objects for the current page:
    results = link_schema.dump(link_query.items, many=True)
    return jsonify(
        total_links=len(user.links),
        page=link_query.page,
        total_pages=link_query.pages,
        next_page=link_query.next_num,
        per_page=per_page,
        links=results
    )
    


@link_bp.route('', methods=['POST'])
@requires_auth(allowed=['jwt', 'api-key'])
def post_link():
    """Creates a new link in the database.
    """
    user = current_user()
    # Collect information via the JSON body of the request
    body = request.get_json()
    if body is None:
        raise InvalidUsage(message="This method expects valid JSON data as the request body")
    # Pass everything to the `create_link` function (data validation
    # will be performed here too)
    link_id = user.create_link(**body)
    new_link = Link.query.get(link_id)
    response = make_response(jsonify(**link_schema.dump(new_link)), 201)
    response.headers['Location'] = url_for('link_bp.get_link', id=link_id)
    return response


@link_bp.route('/<int:id>', methods=['GET'])
@requires_auth(allowed=['jwt', 'api-key'])
def get_link(id):
    """Retrieves and serializes a link at a given ID.
    """
    user = current_user()
    link = Link.query.get_or_404(id)
    AuthService.check_link_access(user.id, link)
    return jsonify(link_schema.dump(link))


@link_bp.route('/<int:id>', methods=['PATCH'])
@requires_auth(allowed=['jwt', 'api-key'])
def update_link(id):
    """Updates any fields on a link that are passed in the JSON
    payload. Other fields are left unmodified.
    """
    user = current_user()
    link = Link.query.get_or_404(id)
    AuthService.check_link_access(user.id, link)
    
    body = request.get_json()
    if body is None:
        raise InvalidUsage(message="This method expects valid JSON data as the request body")
    # Validate the incoming JSON to make sure any changes conform to the schema:
    errors = link_schema.validate(body, partial=True)
    if errors:
        raise ValidationError(message=errors)
    for key, value in body.items():
        if hasattr(link, key) and getattr(link, key) != value:
            # Make a change to the Link object stored in the database
            # if the values actually differ:
            setattr(link, key, value)
    # If we've made any changes, commit them:
    db.session.commit()
    return jsonify(message=f"Link with ID {id} updated successfully"), 200


@link_bp.route('/<int:id>', methods=['DELETE'])
@requires_auth(allowed=['jwt', 'api-key'])
def delete_link(id):
    """Deletes a link by ID.
    """
    user = current_user()
    link = Link.query.get_or_404(id)
    AuthService.check_link_access(user.id, link)

    db.session.delete(link)
    db.session.commit()
    return jsonify(message=f"Link with ID {id} deleted successfully"), 200