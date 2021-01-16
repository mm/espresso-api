"""Various administration/maintenance functions available
over the Flask CLI.
"""

import click
from flask import Blueprint, current_app
from src.model import db, User, Link
from src.auth import generate_api_key, validate_api_key

# You can run these with `flask admin <command here>`:
admin_bp = Blueprint('admin', __name__)

@admin_bp.cli.command('create_db')
def create_db():
    """Creates all database tables."""
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

    if not db.engine.has_table('user'):
        click.echo("Users table hasn't been created yet. Please run flask admin create_db to initialize tables first.", err=True)
        return None

    click.echo("Generating a new user and API key...")
    name = click.prompt("Enter your name (optional)", default='', type=str)
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
        click.echo("User generation failed.", err=True)


@admin_bp.cli.command('rotate_key')
def rotate_user_key():
    """Re-generates an API key."""
    click.echo("This will re-generate your API key.")
    user_id = click.prompt("Specify a user ID", type=int)

    if user_id is None:
        click.echo("User ID is required.", err=True)
        return None

    user = User.query.get(user_id)
    if user is None:
        click.echo("User does not exist.", err=True)
        return None
    
    try:
        key = generate_api_key()
        user.api_key = key.hashed_key
        click.echo(f"New API key is: {key.api_key}")
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Key rotation failed: {e}")
        click.echo("Key rotation failed, please check application logs.")


@admin_bp.cli.command('drop_tables')
def drop_tables():
    """Drops all database tables.
    """
    # If the user responds no here, everything will abort, so we don't need to check the choice:
    click.confirm("This will drop all application tables -- all data will be deleted. Are you sure?", abort=True)
    click.echo("Dropping all tables... ", nl=False)
    try:
        db.metadata.drop_all(db.engine, tables=[Link.__table__, User.__table__])
        click.echo("Complete.")
    except Exception as e:
        current_app.logger.error(f"Error running drop_tables(): {e}")
        click.echo("Error dropping tables, please check application logs.", err=True)