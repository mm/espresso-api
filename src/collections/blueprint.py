from flask import Blueprint, jsonify, request
from src.model import CollectionSchema
from .service import CollectionService
from src.auth.decorators import requires_auth
from src.auth.service import current_user
from src.exceptions import AuthError

collection_bp = Blueprint("collection_bp", __name__)
schema = CollectionSchema()


@collection_bp.route("", methods=["GET"])
@requires_auth(allowed=["api-key", "jwt"])
def get_collections():
    user = current_user()
    collections = CollectionService().get_collections_for_user(user.id)

    return jsonify(schema.dump(collections, many=True))

@collection_bp.route("", methods=["POST"])
@requires_auth(allowed=["api-key", "jwt"])
def create_collection():
    user = current_user()
    body = request.get_json()

    collection_document = schema.load(body)
    CollectionService().create_collection(user.id, collection_document)

    return jsonify(message="Collection created successfully"), 201

@collection_bp.route("/<int:id>", methods=["DELETE"])
@requires_auth(allowed=["api-key", "jwt"])
def archive_collection(id: int):
    user = current_user()
    collection_service = CollectionService()
    collection = collection_service.get_collection(id)
    if not collection:
        return jsonify(message="Collection not found"), 404

    if collection.user_id != user.id:
        raise AuthError("You are not allowed to access this collection", status_code=403)
    
    collection_service.archive_collection(id)
    return jsonify(message="Collection archived successfully"), 200

