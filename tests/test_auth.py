"""Tests on Charlotte Auth functions."""

from hashlib import sha256
import pytest
import src.auth as auth


def test_generate_api_key():
    """Tests to ensure the SHA-256 hash of the generated
    key matches the hash the function saves to the database.
    """

    key = auth.generate_api_key()  # returns a NamedTuple with api_key and hashed_key
    hashed_api_key = sha256(key.api_key.encode('utf-8')).hexdigest()
    assert hashed_api_key == key.hashed_key


@pytest.mark.parametrize(('key', 'result'), (
    ('use-valid-key', True),
    ('abc123', False),
    (None, False),
    ('', False)
))
def test_validate_api_key(app, seed_data, key, result):
    """Ensures a valid API key returns True, and an invalid key
    returns False.
    """
    user_id, api_key = seed_data
    if key == 'use-valid-key':
        key = api_key
    with app.app_context():
        assert auth.validate_api_key(user_id, key) == result


def test_user_for_api_key(app, seed_data):
    """Ensures that the API key lookups used by the decorator
    function works as expected.
    """
    # Get seed data:
    user_id, api_key = seed_data

    with app.app_context():
        user = auth.user_for_api_key(api_key)
        assert user.id == user_id
