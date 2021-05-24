from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask, g
from celery import Celery
from flask_limiter import Limiter
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter.util import get_remote_address
from dotenv import find_dotenv, load_dotenv
import src.handlers as handlers
from src.exceptions import InvalidUsage, AuthError
from .config import CeleryConfig

# If we have .env files present, load them:
if find_dotenv():
    load_dotenv()

migrate = Migrate()
celery = Celery(__name__, broker=CeleryConfig.broker_url)


def create_app(config="src.config.DevConfig", test_config=None):
    """The application factory for Espresso. Sets up configuration
    parameters, sets up the database connection and hooks up the view
    blueprints for all the API routes.

    Arguments:
    - config: The class object to configure Flask from
    - test_config: Key-value mappings to override common configuration (i.e. for
    running unit tests and overriding the database URI)
    """
    from src.general import general_bp
    from src.cli import admin_bp
    from src.auth.blueprint import auth_bp
    from src.links.blueprint import link_bp
    from src.importer.blueprint import importer_bp
    from src.collections.blueprint import collection_bp

    app = Flask(__name__)
    # Load configuration from an object. Note that all sensitive values
    # are fetched from environment variables (see config.py):
    app.config.from_object(config)
    celery.config_from_object("src.config.CeleryConfig")
    # Override anything we need to for unit tests:
    if test_config:
        app.config.from_mapping(test_config)

    # Bind Flask-SQLAlchemy and Flask-Migrate:
    from src.model import db, User, Link

    db.init_app(app)
    migrate.init_app(app, db, directory="alembic")

    # Set up rate limiting on all API routes:
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["5 per second", "150 per day"],
    )
    limiter.limit(link_bp)
    limiter.limit(auth_bp)
    limiter.limit(general_bp)
    # Enable CORS on all endpoints:
    CORS(app)
    # Register all of our view functions with the app:
    app.register_blueprint(general_bp, url_prefix="/v1")
    app.register_blueprint(auth_bp, url_prefix="/v1/auth")
    app.register_blueprint(link_bp, url_prefix="/v1/links")
    app.register_blueprint(importer_bp, url_prefix="/v1/import")
    app.register_blueprint(collection_bp, url_prefix="/v1/collections")
    app.register_blueprint(admin_bp)
    app.teardown_appcontext(teardown_handler)
    # Register error handlers shared across all routes:
    app.register_error_handler(404, handlers.handle_not_found)
    app.register_error_handler(500, handlers.handle_server_error)
    app.register_error_handler(InvalidUsage, handlers.handle_invalid_data)
    app.register_error_handler(SQLAlchemyError, handlers.handle_sqa_general)
    app.register_error_handler(ValidationError, handlers.handle_validation_error)
    app.register_error_handler(AuthError, handlers.handle_auth_error)

    return app


def teardown_handler(exception):
    g.current_user = None
    if "current_uid" in g:
        g.current_uid = None
