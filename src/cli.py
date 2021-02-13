"""Various administration/maintenance functions available
over the Flask CLI.
"""

import click
from flask import Blueprint, current_app
from src.model import db, User, Link
from src.seed import seed_dummy_data, seed_user

# You can run these with `flask admin <command here>`:
admin_bp = Blueprint('admin', __name__)


@admin_bp.cli.command('new_user')
@click.option('--name', default='Tester', help='Name of the user to create')
def new_user(name):
    """Creates a new user with an API key.
    """
    seed_user(name=name)


@admin_bp.cli.command('dummy')
def dummy_data():
    """Creates a dummy testing environment, complete
    with a test user and links.
    """
    seed_dummy_data()


@admin_bp.cli.command('clear_tables')
def clear_tables():
    """Deletes all data.
    """
    click.confirm("This will delete all data in the database tables without dropping the tables themselves. Are you sure?", abort=True)
    click.echo("Deleting all data...", nl=False)
    try:
        db.engine.execute('delete from "link"')
        db.engine.execute('delete from "user"')
        click.echo('Complete')
    except Exception as e:
        current_app.logger.error(f"Error running drop_tables(): {e}")
        click.echo("Error dropping tables, please check application logs.", err=True)    


@admin_bp.cli.command('drop_tables')
def drop_tables():
    """Drops all database tables.
    """
    # If the user responds no here, everything will abort, so we don't need to check the choice:
    click.confirm("This will drop all application tables -- all data will be deleted. Are you sure?", abort=True)
    click.echo("Dropping all tables... ", nl=False)
    try:
        db.engine.execute('drop table alembic_version;')
        db.engine.execute('drop table "link"')
        db.engine.execute('drop table "user"')
        click.echo("Complete.")
    except Exception as e:
        current_app.logger.error(f"Error running drop_tables(): {e}")
        click.echo("Error dropping tables, please check application logs.", err=True)