"""Stores pytest fixtures to be used across multiple unit tests.
"""

import os

os.environ["DB_DATABASE"] = "espresso_test"
os.environ["FIREBASE_ENABLED"] = "0"

import pytest
from src import create_app
from flask_migrate import upgrade
from sqlalchemy import text
from src.model import db
from src.manager import seed


@pytest.fixture
def app():
    app = create_app("src.config.TestConfig")
    with app.app_context():
        # Run migrations:
        upgrade(directory="alembic")
    yield app

    # Once the app fixture is no longer needed, drop the tables:
    with app.app_context():
        db.engine.execute(text('drop table link, "user", alembic_version;'))


@pytest.fixture(scope="module")
def scoped_app():
    """Gives access to an app context for an entire module's duration,
    and tears down DB structure afterwards.
    """
    app = create_app("src.config.TestConfig")
    with app.app_context():
        # Run migrations:
        upgrade(directory="alembic")
        yield app

    # Once the app fixture is no longer needed, drop the tables:
    with app.app_context():
        db.engine.execute(text('drop table link, "user", alembic_version;'))


@pytest.fixture
def seed_data(app):
    with app.app_context():
        user_id, api_key = seed.seed_self(name="Matt", email="matt@example.com")
        seed.seed_links(user_id)
    return user_id, api_key


@pytest.fixture
def client(app):
    """Testing client for validating API requests and responses"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Test CLI runner to test admin CLI commands"""
    return app.test_cli_runner()
