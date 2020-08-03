"""Blueprint containing API routes for Untitled. All
routes will be prefixed with /api.
"""

from flask import Blueprint, jsonify, request, make_response, url_for, current_app
from sqlalchemy.exc import SQLAlchemyError
from untitled.model import db, Link, UserSchema, LinkSchema
from marshmallow import ValidationError
from untitled.auth import api_key_auth
from untitled.exceptions import InvalidUsage

api_bp = Blueprint('api_bp', __name__)

@api_bp.errorhandler(InvalidUsage)
def handle_invalid_data(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@api_bp.errorhandler(404)
def handle_not_found(error):
    return jsonify(error="Requested resource was not found in the database"), 404

@api_bp.errorhandler(500)
def handle_server_error(error):
    return jsonify(error="An unknown error while accessing resource"), 500

@api_bp.errorhandler(SQLAlchemyError)
def handle_sqa_general(error):
    """Catch-all for any SQLAlchemy error we haven't caught explicitly already"""
    current_app.logger.error(f"Database error: {error}")
    return jsonify(error="An error occured while communicating with the database"), 500

@api_bp.errorhandler(ValidationError)
def handle_validation_error(error):
    """Catches exceptions related to data validation in Marshmallow"""
    return jsonify(error="The submitted data failed validation checks", issues=error.messages), 422


@api_bp.route('/user', methods=['GET'])
@api_key_auth
def user(current_user=None):
    """Returns information about the user (authenticated via API key).
    """
    # Pull only the user ID and name from the users table:
    user_details = UserSchema().dump(current_user)
    return jsonify(
        **user_details,
        links=len(current_user.links)
    ), 200


@api_bp.route('/links', methods=['GET', 'POST'])
@api_key_auth
def links(current_user=None):
    """Returns a list of links for the current user (and pointers
    to another page of links), or allows for the creation of new
    links (data received in JSON payload)
    """
    schema = LinkSchema()
    if request.method == 'GET':
        
        # Default to page 1, with 20 URLs per page:
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
        except ValueError:
            raise InvalidUsage(message="The page and per_page parameters must be integers")

        link_query = Link.query.filter(Link.user_id==current_user.id).order_by(Link.date_added).paginate(
            page=page, per_page=per_page
        )
        # Here, `items` is the Link objects for the current page:
        results = [schema.dump(link) for link in link_query.items]
        return jsonify(
            total_links=len(current_user.links),
            page=link_query.page,
            total_pages=link_query.pages,
            next_page=link_query.next_num,
            per_page=per_page,
            links=results
        )

    # Otherwise, we're creating a new link
    # Collect information via the JSON body of the request
    body = request.get_json()
    if body:
        # Pass everything to the `create_link` function (anything extranneous will
        # be ignored):
        link_id = current_user.create_link(**body)
        new_link = Link.query.get(link_id)
        response = make_response(jsonify(**schema.dump(new_link)), 201)
        response.headers['Location'] = url_for('api_bp.link', id=link_id)
        return response
    else:
        raise InvalidUsage(message="This method expects valid JSON data as the request body")


@api_bp.route('/links/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@api_key_auth
def link(id, current_user=None):
    """Methods for fetching, updating or deleting a link.
    """
    schema = LinkSchema()
    # Calling .first_or_404() will automatically yield a 404 if no
    # item was found (we registered an exception handler to catch this)
    link = Link.query.get_or_404(id)
    # Check: does the current user even have permission to access
    # the link?
    if link.user_id != current_user.id:
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
        for key, value in body.items():
            # TODO: Validate input (will currently raise exception, but could be prettier)
            if hasattr(link, key) and getattr(link, key) != value:
                # If the Link object *has* the attribute described in
                # the request, and the value in the request is different
                # than what's stored in the database, change the value in
                # the database:
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