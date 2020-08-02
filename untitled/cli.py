"""Various administration/maintenance functions available
over the Flask CLI.
"""

import click
from flask import Blueprint
from untitled.model import db, User
from untitled.auth import generate_api_key, validate_api_key

# You can run these with `flask admin <command here>`:
admin_bp = Blueprint('admin', __name__)

@admin_bp.cli.command('create_db')
def create_db():
    """Initializes the database (if tables already
    exist, they won't be re-created)
    """
    print("Creating database...")
    db.create_all()


@admin_bp.cli.command('create_user')
def create_user():
    """Adds a new user to the database and generates an
    API key.
    """
    print("Generating a new user and API key...")
    name = str(input("Name: "))
    key = generate_api_key()

    try:
        new_user = User(name=name, api_key=key.hashed_key)
        db.session.add(new_user)
        db.session.commit()
        print("Created new user! Below are the user details:")
        print(f"Name: {new_user.name}")
        print(f"User ID: {new_user.id}")
        print(f"API Key: {key.api_key}")
        print("Please write down the API key as it will only appear once!")
    except Exception as e:
        # TODO: This needs much better error handling -- should handle DB errors separately.
        print("User generation failed.")