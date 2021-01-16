"""Various administration/maintenance functions available
over the Flask CLI.
"""

import click
from flask import Blueprint, current_app
from src.model import db, User, Link
from src.auth import generate_api_key, validate_api_key
from src.seed import seed_dummy_data, seed_user

# You can run these with `flask admin <command here>`:
admin_bp = Blueprint('admin', __name__)


@admin_bp.cli.command('create_user')
def create_user():
    """Adds a new user to the database and generates an
    API key.
    """

    if not db.engine.has_table('user'):
        click.echo("Users table hasn't been created yet. Please run flask db migrate to initialize tables first.", err=True)
        return None

    click.echo("Generating a new user and API key...")
    seed_user()


@admin_bp.cli.command('dummy')
def dummy_data():
    """Creates a dummy testing environment.
    """
    seed_dummy_data()


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