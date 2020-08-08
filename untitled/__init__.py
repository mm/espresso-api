import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from untitled.api import api_bp
from untitled.cli import admin_bp

def create_app(config='dev'):
    """The application factory for Untitled. Sets up configuration
    parameters, sets up the database connection and hooks up the view
    blueprints for all the API routes.
    """

    app = Flask(__name__)
    if config == 'stg':
        # Helper for still loading .env files if testing Gunicorn locally:
        load_dotenv()
    elif config == 'testing':
        app.config['TESTING'] = True
    # Required by SQLAlchemy -- for local development this is
    # loaded in via a .env file:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from untitled.model import db
    db.init_app(app)
    # Set up rate limiting on all API routes:
    limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["5 per second", "150 per day"])
    limiter.limit(api_bp)
    # Register all of our view functions with the app:
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp)
    return app
