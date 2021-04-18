"""Stores pytest fixtures to be used across multiple unit tests.
"""

import os

os.environ["DB_DATABASE"] = "espresso_test"
os.environ["FIREBASE_ENABLED"] = "0"

import pytest
from src import create_app
from flask_migrate import upgrade
from sqlalchemy import text
from src.model import db, User
from src.manager import seed
from src.auth.service import AuthService
from .factories import UserFactory
from typing import Tuple


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
def client(app):
    """Testing client for validating API requests and responses"""
    return app.test_client()


@pytest.fixture(scope="module")
def scoped_client(scoped_app):
    """Test client that persists throughout a module."""
    return scoped_app.test_client()


@pytest.fixture
def test_user(scoped_app) -> Tuple[User, str]:
    """Creates a user and returns a tuple containing the
    User object, and an API key to access their resources
    for the scope of the test.
    """
    user = UserFactory()
    api_pair = AuthService.generate_api_key()
    user.api_key = api_pair.hashed_key
    return (user, api_pair.api_key)


@pytest.fixture
def runner(app):
    """Test CLI runner to test admin CLI commands"""
    return app.test_cli_runner()
