import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from untitled.api import api_bp
from untitled.cli import admin_bp

def create_app():
    """The application factory for Untitled. Sets up configuration
    parameters, sets up the database connection and hooks up the view
    blueprints for all the API routes.
    """

    app = Flask(__name__)
    # Required by SQLAlchemy -- for local development this is
    # loaded in via a .env file:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from untitled.model import db
    db.init_app(app)
    # Register all of our view functions with the app:
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp)
    return app
