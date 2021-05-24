from flask import Blueprint, jsonify
from src.model import CollectionSchema

collection_bp = Blueprint("collection_bp", __name__)
schema = CollectionSchema()


@collection_bp.route("", methods=["GET"])
def hello():
    return jsonify(message="Hello")
