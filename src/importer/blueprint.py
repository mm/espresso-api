from flask import Blueprint, jsonify, request
from src.auth.decorators import requires_auth
from src.auth.service import current_user
from .service import JSONImporter

importer_bp = Blueprint('importer_bp', __name__)


@importer_bp.route('/json', methods=['POST'])
@requires_auth(allowed=['jwt', 'api-key'])
def post_json_import():
    """Imports a JSON file full of links. JSON is one of the standard formats
    this app exports for a backup.
    """
    user = current_user()
    importer = JSONImporter()
    links = request.get_json().get('links')
    transformed_links = importer.transform_links(links, user_id=user.id)
    import_results = importer.load_links(transformed_links)

    return jsonify(
        message='Import complete', 
        links_imported=import_results.imported,
        errors=import_results.errors
    )
