"""Various administration/maintenance functions available
over the Flask CLI.
"""

import click
from flask import Blueprint
from untitled.model import db

# You can run these with `flask admin <command here>`:
admin_bp = Blueprint('admin', __name__)

@admin_bp.cli.command('create_db')
def create_db():
    """Initializes the database.
    """
    db.create_all()


@admin_bp.cli.command('create_user')
def create_user():
    """Adds a new user to the database and generates an
    API key.
    """
    pass