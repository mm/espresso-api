"""Stores pytest fixtures to be used across multiple unit tests.
"""

import os
import tempfile

import pytest
from src import create_app
from flask_migrate import upgrade
from src.model import db
from src.seed import seed_user, seed_links

@pytest.fixture
def app():
    # We're going to be using a SQLite local database to test
    # out anything requiring a database (this app doesn't use
    # anything Postgres-specific so this should be safe)

    # Set up a temporary file pointer and use the URL to set
    # the location of our temporary DB:
    db_fd, db_url = tempfile.mkstemp()
    app = create_app('src.config.TestConfig', test_config={
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///'+db_url
    })

    with app.app_context():
        # Run migrations:
        upgrade(directory='alembic')

    yield app
    
    os.close(db_fd)
    os.unlink(db_url)


@pytest.fixture
def seed_data(app):
    with app.app_context():
        user_id = seed_user()
        seed_links(user_id)
    return user_id


@pytest.fixture
def client(app):
    """Testing client for validating API requests and responses"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Test CLI runner to test admin CLI commands"""
    return app.test_cli_runner()
