import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter.util import get_remote_address
from dotenv import find_dotenv, load_dotenv
from src.api import api_bp

migrate = Migrate()

def create_app(config='src.config.DevConfig', test_config=None):
    """The application factory for Charlotte. Sets up configuration
    parameters, sets up the database connection and hooks up the view
    blueprints for all the API routes.

    Arguments:
    - config: The class object to configure Flask from
    - test_config: Key-value mappings to override common configuration (i.e. for
    running unit tests and overriding the database URI)
    """

    # If we have .env files present, load them:
    if find_dotenv():
        load_dotenv()

    app = Flask(__name__)
    # Load configuration from an object. Note that all sensitive values
    # are fetched from environment variables (see config.py):
    app.config.from_object(config)
    # Override anything we need to for unit tests:
    if test_config:
        app.config.from_mapping(test_config)

    # Bind Flask-SQLAlchemy and Flask-Migrate:
    from src.model import db, User, Link
    db.init_app(app)
    migrate.init_app(app, db, directory='alembic')

    # Set up rate limiting on all API routes:
    limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["5 per second", "150 per day"])
    limiter.limit(api_bp)
    # Enable CORS on all endpoints:
    CORS(app)
    # Register all of our view functions with the app:
    app.register_blueprint(api_bp, url_prefix='/api')
    return app
