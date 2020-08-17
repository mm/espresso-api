"""Tests on the Charlotte CLI."""

import pytest
from charlotte.cli import create_db, create_user
from charlotte.auth import validate_api_key
from charlotte.model import db

def test_database_creation(app, runner):
    """Tests the ability to create table structure from the CLI.
    """
    result = runner.invoke(create_db)
    assert not result.exception
    assert 'Creating table structure...' in result.output
    assert 'Tables have been created.' in result.output

    # Were our tables actually created?
    with app.app_context():
        assert db.engine.has_table('user')
        assert db.engine.has_table('link')


def test_user_creation(app, runner):
    """Tests the ability to generate an API key from the CLI.
    """
    result = runner.invoke(create_user, input="TestMatt\n")
    assert not result.exception
    output_lines = result.output.split('\n')

    assert output_lines[2] == 'Created new user! Below are the user details:'
    output_name = output_lines[3].split(' ')[1]  # 'Name: TestMatt' originally
    output_id = output_lines[4].split(' ')[2]  # User ID: 2 originally
    output_key = output_lines[5].split(' ')[2]  # API Key: ______ originally
    
    assert output_name == 'TestMatt'
    assert output_id == '2'

    # Can our user actually log in with the API key given?
    with app.app_context():
        assert validate_api_key(output_id, output_key)
