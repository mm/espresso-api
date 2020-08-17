"""Various administration/maintenance functions available
over the Flask CLI.
"""

import click
from flask import Blueprint, current_app
from charlotte.model import db, User
from charlotte.auth import generate_api_key, validate_api_key

# You can run these with `flask admin <command here>`:
admin_bp = Blueprint('admin', __name__)

@admin_bp.cli.command('create_db')
def create_db():
    """Initializes the database (if tables already
    exist, they won't be re-created)
    """
    click.echo("Creating table structure...")
    try:
        db.create_all()
        click.echo("Tables have been created.")
    except Exception as e:
        current_app.logger.error(f'Error during create_db(): {e}')
        click.echo("Issue creating the database, please check application logs.", err=True)


@admin_bp.cli.command('create_user')
def create_user():
    """Adds a new user to the database and generates an
    API key.
    """
    click.echo("Generating a new user and API key...")
    name = click.prompt("Please enter your name", type=str)
    key = generate_api_key()

    try:
        new_user = User(name=name, api_key=key.hashed_key)
        db.session.add(new_user)
        db.session.commit()
        click.echo("Created new user! Below are the user details:")
        click.echo(f"Name: {new_user.name}")
        click.echo(f"User ID: {new_user.id}")
        click.echo(f"API Key: {key.api_key}")
        click.echo("Please write down the API key as it will only appear once!")
    except Exception as e:
        # TODO: This needs much better error handling -- should handle DB errors separately.
        current_app.logger.error(f'Error during create_user(): {e}')
        print("User generation failed.")


@admin_bp.cli.command('rotate_key')
def rotate_user_key():
    """Re-generates a user's API key given the previous one.
    """
    click.echo("This will re-generate your API key.")
    user_id = click.prompt("Specify a user ID", type=int)
    existing_key = click.prompt("Existing API key", type=str)

    if user_id is None or existing_key is None:
        click.echo("User ID and API key are required.", err=True)
        return None

    user = User.query.get(user_id)
    if user is None:
        click.echo("User does not exist.", err=True)
        return None
    
    if validate_api_key(user_id, existing_key):
        key = generate_api_key()
        user.api_key = key.hashed_key
        click.echo(f"New API key is: {key.api_key}")
        db.session.commit()
    else:
        click.echo("API key validation failed.", err=True)
