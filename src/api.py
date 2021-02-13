"""Blueprint containing API routes for Charlotte. All
routes will be prefixed with /api.
"""

from flask import Blueprint, jsonify, request, make_response, url_for
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from src.model import db, Link, UserSchema, LinkSchema
from src.auth.service import current_user
from src.auth.decorators import requires_auth
from src.exceptions import InvalidUsage, AuthError
import src.handlers as handlers

api_bp = Blueprint('api_bp', __name__)

#  Exception handlers:
api_bp.register_error_handler(404, handlers.handle_not_found)
api_bp.register_error_handler(500, handlers.handle_server_error)
api_bp.register_error_handler(InvalidUsage, handlers.handle_invalid_data)
api_bp.register_error_handler(SQLAlchemyError, handlers.handle_sqa_general)
api_bp.register_error_handler(ValidationError, handlers.handle_validation_error)
api_bp.register_error_handler(AuthError, handlers.handle_auth_error)


@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify(message='API is online'), 200


#  /user routes:
@api_bp.route('/user', methods=['GET'])
@requires_auth
def user():
    """Returns information about the user to display on the UI.
    """
    user = current_user()
    user_details = UserSchema().dump(user)
    return jsonify(
        **user_details,
        links=len(user.links)
    ), 200


# /links routes:
@api_bp.route('/links', methods=['GET', 'POST'])
@requires_auth
def links():
    """Returns a list of links for the current user (and pointers
    to another page of links), or allows for the creation of new
    links (data received in JSON payload). The `show` URL param controls
    whether archived links are returned, and can be one of `all`, `read`,
    or `unread` (default "unread")
    """
    schema = LinkSchema()
    user = current_user()
    if request.method == 'GET':
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
        results = schema.dump(link_query.items, many=True)
        return jsonify(
            total_links=len(user.links),
            page=link_query.page,
            total_pages=link_query.pages,
            next_page=link_query.next_num,
            per_page=per_page,
            links=results
        )

    # Otherwise, we're creating a new link (POST):
    # Collect information via the JSON body of the request
    body = request.get_json()
    if body is None:
        raise InvalidUsage(message="This method expects valid JSON data as the request body")
    # Pass everything to the `create_link` function (data validation
    # will be performed here too)
    link_id = user.create_link(**body)
    new_link = Link.query.get(link_id)
    response = make_response(jsonify(**schema.dump(new_link)), 201)
    response.headers['Location'] = url_for('api_bp.link', id=link_id)
    return response


@api_bp.route('/links/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@requires_auth
def link(id):
    """Methods for fetching, updating or deleting a link.
    """
    schema = LinkSchema()
    user = current_user()
    # Calling .first_or_404() will automatically yield a 404 if no
    # item was found (we registered an exception handler to catch this)
    link = Link.query.get_or_404(id)
    # Check: does the current user even have permission to access
    # the link?
    if link.user_id != user.id:
        # You shall not pass
        raise InvalidUsage(message="You are not authorized to access this item", status_code=403)

    if request.method == 'GET':
        return jsonify(schema.dump(link))
    elif request.method == 'PATCH':
        # Update a field or two in the link, based on the payload. Really,
        # all we can modify is the title, the URL or the read status (or
        # a combination of all three)
        body = request.get_json()
        if body is None:
            raise InvalidUsage(message="This method expects valid JSON data as the request body")
        # Validate the incoming JSON to make sure any changes conform to the schema:
        errors = schema.validate(body, partial=True)
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
    elif request.method == 'DELETE':
        # Cast the link out of existence!
        db.session.delete(link)
        db.session.commit()
        return jsonify(message=f"Link with ID {id} deleted successfully"), 200
    else:
        raise InvalidUsage(message="Method not allowed for this resource", status_code=405)
