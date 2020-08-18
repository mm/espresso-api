"""Tests on Charlotte Auth functions."""

from hashlib import sha256
import pytest
import charlotte.auth as auth

# We know this key in advance because of how we seeded the database tables
VALID_KEY = '204764892964d5931312b50f280a0112286f4ebb07111a65f7a1cb238437322d'
INVALID_KEY = '99ca17a0a2348dca9280668bb0de604b9d3eea93595e9e85e35e2a88f1c77eb3'

def test_generate_api_key():
    """Tests to ensure the SHA-256 hash of the generated
    key matches the hash the function saves to the database.
    """

    key = auth.generate_api_key()  # returns a NamedTuple with api_key and hashed_key
    hashed_api_key = sha256(key.api_key.encode('utf-8')).hexdigest()
    assert hashed_api_key == key.hashed_key


@pytest.mark.parametrize(('key', 'result'), (
    (VALID_KEY, True),
    (INVALID_KEY, False),
    (None, False),
    ('', False)
))
def test_validate_api_key(app, key, result):
    """Ensures a valid API key returns True, and an invalid key
    returns False.
    """
    with app.app_context():
        assert auth.validate_api_key(1, key) == result


@pytest.mark.parametrize(('key', 'user_id'), (
    (VALID_KEY, 1),
    (INVALID_KEY, None),
    ('', None),
    (None, None)
))
def test_user_for_api_key(app, key, user_id):
    """Ensures that the API key lookups used by the decorator
    function works as expected.
    """
    with app.app_context():
        user = auth.user_for_api_key(key)
        # If we're expecting None, check for None-ness. Otherwise,
        # go straight for the user's ID, which should be 1.
        if user_id:
            assert user.id == user_id
        else:
            assert user is None
