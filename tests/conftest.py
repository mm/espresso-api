"""Stores pytest fixtures to be used across multiple unit tests.
"""

import os
import tempfile

import pytest
from src import create_app
from flask_migrate import upgrade
from sqlalchemy import text
from src.model import db
from src.seed import seed_user, seed_links

@pytest.fixture
def app():
    # TODO: Better way of setting this variable
    os.environ['DB_DATABASE'] = 'charlotte_test'
    os.environ['TESTING'] = '1'
    app = create_app('src.config.TestConfig')

    with app.app_context():
        # Run migrations:
        upgrade(directory='alembic')

    yield app
    
    # Once the app fixture is no longer needed, drop the tables:
    with app.app_context():
        db.engine.execute(text('drop table link, "user", alembic_version;'))


@pytest.fixture
def seed_data(app):
    with app.app_context():
        user_id, api_key = seed_user()
        seed_links(user_id)
    return user_id, api_key


@pytest.fixture
def client(app):
    """Testing client for validating API requests and responses"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Test CLI runner to test admin CLI commands"""
    return app.test_cli_runner()
