"""Blueprint for all endpoints that manipulate individual links.
"""

from flask import Blueprint, jsonify, request, make_response, url_for
from marshmallow import ValidationError
from src.auth.service import AuthService, current_user
from .service import LinkService
from src.model import LinkSchema, LinkQuerySchema, MultipleLinkSchema
from src.auth.decorators import requires_auth


link_bp = Blueprint("link_bp", __name__)
link_schema = LinkSchema()


@link_bp.route("", methods=["GET"])
@requires_auth(allowed=["jwt", "api-key"])
def get_links():
    """Returns a list of links for the current user (and pointers
    to another page of links) The `show` URL param controls
    whether archived links are returned, and can be one of `all`, `read`,
    or `unread` (default "unread")
    """
    user = current_user()
    link_service = LinkService()

    # Validate query parameters, setting defaults if necessary:
    query_params = LinkQuerySchema().load(
        {
            "page": request.args.get("page", 1),
            "per_page": request.args.get("per_page", 20),
            "show": request.args.get("show", "unread"),
            "collection": request.args.get("collection"),
        }
    )

    # Return a response with the fetched links, and pagination
    # information as well for the next request:
    link_response = link_service.get_many_links(user.id, query_params)
    # Serialize according to schema:
    return jsonify(MultipleLinkSchema().dump(link_response))


@link_bp.route("", methods=["POST"])
@requires_auth(allowed=["jwt", "api-key"])
def post_link():
    """Creates a new link in the database."""
    link_service = LinkService()
    user = current_user()
    # Collect information via the JSON body of the request
    body = request.get_json()
    if body:
        body["user_id"] = user.id
    link = link_service.create_link(link_schema.load(body))

    response = make_response(link_schema.dump(link), 201)
    response.headers["Location"] = url_for("link_bp.get_link", id=link.id)
    return response


@link_bp.route("/<int:id>", methods=["GET"])
@requires_auth(allowed=["jwt", "api-key"])
def get_link(id):
    """Retrieves and serializes a link at a given ID."""
    user = current_user()
    link = LinkService().get_link(id)
    AuthService.check_link_access(user.id, link)
    return jsonify(link_schema.dump(link))


@link_bp.route("/<int:id>", methods=["PATCH"])
@requires_auth(allowed=["jwt", "api-key"])
def update_link(id):
    """Updates any fields on a link that are passed in the JSON
    payload. Other fields are left unmodified.
    """
    user = current_user()
    link_service = LinkService()
    link = link_service.get_link(id)
    AuthService.check_link_access(user.id, link)

    body = request.get_json()
    # Validate the incoming JSON to make sure any changes conform to the schema:
    errors = link_schema.validate(body, partial=True)
    if errors:
        raise ValidationError(message=errors)
    if "collection_id" in body and (body["collection_id"] == ""):
        body["collection_id"] = None
    link_service.update_link(link, changes=body)

    return (
        jsonify(
            message=f"Link with ID {id} updated successfully",
            link=link_schema.dump(link),
        ),
        200,
    )


@link_bp.route("/<int:id>", methods=["DELETE"])
@requires_auth(allowed=["jwt", "api-key"])
def delete_link(id):
    """Deletes a link by ID."""
    user = current_user()
    link_service = LinkService()
    link = link_service.get_link(id)
    AuthService.check_link_access(user.id, link)
    link_service.delete_link(link)
    return jsonify(message=f"Link with ID {id} deleted successfully"), 200
