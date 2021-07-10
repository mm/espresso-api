"""Various administration/maintenance functions available
over the Flask CLI.
"""

from typing import Optional
import click
from flask import Blueprint, current_app
from src.model import db
import src.manager.seed as seed

# You can run these with `flask admin <command here>`:
admin_bp = Blueprint("admin", __name__)


@admin_bp.cli.command("new_user")
@click.option("--name", default="Tester", help="Name of the user to create")
@click.option("--email", default="test@example.com", help="Email of new user to create")
@click.option("--uid", default=None, help="Firebase UID, if user exists in Firebase Auth already")
def new_user(email: str, name: str, uid: Optional[str]):
    """Creates a new user with an API key."""
    user_id, api_key = seed.seed_self(email=email, name=name, external_uid=uid)
    click.echo("User created:")
    click.echo(f"User ID: {user_id}")
    click.echo(f"API Key: {api_key}")


@admin_bp.cli.command("dummy")
@click.option("--email", type=str, default=None, help="Your email")
@click.option("--name", type=str, default=None, help="Your name")
@click.option("--users", type=int, default=30, help="Number of dummy users to create")
@click.option("--links", type=int, default=30, help="Number of dummy links per user")
def dummy_data(email: str, name: str, users: int, links: int):
    """Generates a testing environment full of fake data. Optionally generates a record
    with your email address as well and an API key to access the account.
    """
    # Seed dummy users:
    dummy_users = seed.seed_fake_users(num_users=users)
    for dummy_user in dummy_users:
        seed.seed_links(user_id=dummy_user.id, num_links=links)
    click.echo(f"Seeding complete. {len(dummy_users)} users added.")
    # If an email was provided, seed one more and return the API key:
    if email:
        user_id, api_key = seed.seed_self(email=email, name=name)
        seed.seed_links(user_id=user_id)
        click.echo("Your user details:")
        click.echo(f"User ID: {user_id}")
        click.echo(f"API Key: {api_key}")


@admin_bp.cli.command("clear_tables")
def clear_tables():
    """Deletes all data."""
    click.confirm(
        "This will delete all data in the database tables without dropping the tables themselves. Are you sure?",
        abort=True,
    )
    click.echo("Deleting all data...", nl=False)
    try:
        db.engine.execute('delete from "link"')
        db.engine.execute('delete from "user"')
        click.echo("Complete")
    except Exception as e:
        current_app.logger.error(f"Error running drop_tables(): {e}")
        click.echo("Error dropping tables, please check application logs.", err=True)


@admin_bp.cli.command("drop_tables")
def drop_tables():
    """Drops all database tables."""
    # If the user responds no here, everything will abort, so we don't need to check the choice:
    click.confirm(
        "This will drop all application tables -- all data will be deleted. Are you sure?",
        abort=True,
    )
    click.echo("Dropping all tables... ", nl=False)
    try:
        db.engine.execute("drop table alembic_version;")
        db.engine.execute('drop table "link"')
        db.engine.execute('drop table "user"')
        click.echo("Complete.")
    except Exception as e:
        current_app.logger.error(f"Error running drop_tables(): {e}")
        click.echo("Error dropping tables, please check application logs.", err=True)
