"""Tests on the Charlotte CLI."""

import pytest
from src.cli import drop_tables
from src.auth import validate_api_key
from src.model import db


def test_table_drop(app, runner):
    """Tests the ability to drop tables from the CLI.
    """
    result = runner.invoke(drop_tables, input="y")

    with app.app_context():
        assert not db.engine.has_table('link')
        assert not db.engine.has_table('user')