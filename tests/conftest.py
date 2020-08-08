"""Stores pytest fixtures to be used across multiple unit tests.
"""

import os
import tempfile

import pytest
from untitled import create_app
from untitled.model import db

# Seed the database with a user and one link associated to them to start out:
# (Also, SQLite complains when you execute multiple statements in one file so
# we break it up here):
with open(os.path.join(os.path.dirname(__file__), "seed_user.sql"), "rb") as f:
    seed_user_sql = f.read().decode('utf-8')

with open(os.path.join(os.path.dirname(__file__), "seed_link.sql"), "rb") as f:
    seed_link_sql = f.read().decode('utf-8')

@pytest.fixture
def app():
    # We're going to be using a SQLite local database to test
    # out anything requiring a database (this app doesn't use
    # anything Postgres-specific so this should be safe)

    # Set up a temporary file pointer and use the URL to set
    # the location of our temporary DB:
    db_fd, db_url = tempfile.mkstemp()
    os.environ['DATABASE_URL'] = 'sqlite:///'+db_url
    os.environ['FLASK_APP'] = 'untitled'
    app = create_app('testing')

    with app.app_context():
        # Create all tables in the model:
        db.create_all()
        db.engine.execute(seed_user_sql)
        db.engine.execute(seed_link_sql)

    yield app
    
    os.close(db_fd)
    os.unlink(db_url)


@pytest.fixture
def client(app):
    """Testing client for validating API requests and responses"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Test CLI runner to test admin CLI commands"""
    return app.test_cli_runner()
