from src.model import User
import pytest
from .factories import UserFactory, LinkFactory
from src.auth.service import AuthService, AuthError
from unittest.mock import patch


def test_check_link_access_positive(scoped_app):
    """If a user owns the link about to be checked, the
    check_link_access should return True.
    """

    link = LinkFactory()
    user_id = link.user_id

    assert AuthService.check_link_access(user_id, link)


def test_check_link_access_negative(scoped_app):
    """If a user does *not* own the link about to be accessed,
    the link access check should raise an AuthError.
    """

    link = LinkFactory()
    user = UserFactory()

    with pytest.raises(AuthError):
        AuthService.check_link_access(user.id, link)


def test_validate_api_key_positive(scoped_app):

    user = UserFactory()
    api_pair = AuthService.generate_api_key()
    user.api_key = api_pair.hashed_key  # we only save hashed API keys in the DB
    assert AuthService.validate_api_key(user.id, api_pair.api_key)


def test_validate_api_key_negative(scoped_app):
    user = UserFactory()
    assert AuthService.validate_api_key(user.id, 'NOT_YO_KEY') == False


def test_user_for_api_key(scoped_app):
    user = UserFactory()
    api_pair = AuthService.generate_api_key()
    user.api_key = api_pair.hashed_key

    returned_user = AuthService.user_for_api_key(api_pair.api_key)

    assert returned_user == user


def test_associate_external_user_existing_user(scoped_app):
    """When a new user is added in Firebase Auth with the same email as one
    in our local database, the Firebase UID should sync over to the database.
    """

    with patch('src.auth.firebase.FirebaseService.user_info_at_uid') as user_at_uid:
        # Create a new user with a specific email:
        user = UserFactory(email='matt@example.xyz')
    
        # Prepare a response from Firebase indicating a user added with this email:
        user_at_uid.return_value = {
            'uid': 'abc1234',
            'name': 'MattTheTest',
            'email': 'matt@example.xyz'
        }

        # Attach the Firebase user ID to our internal user record:
        AuthService.associate_external_user('abc1234')

        # Verify the external UID synced over from Firebase
        assert user.external_uid == 'abc1234'