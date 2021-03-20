from tests.factories import UserFactory, LinkFactory
from src.links.service import LinkService
from werkzeug.exceptions import NotFound
import pytest


def test_get_link(scoped_app):
    new_link = LinkFactory()
    id_that_exists = new_link.id
    id_that_does_not_exist = 666

    assert LinkService().get_link(id_that_exists) == new_link

    # Assert links that don't exist raise a 404 exception:
    with pytest.raises(NotFound):
        LinkService().get_link(id_that_does_not_exist)


def test_update_link(scoped_app):
    link = LinkFactory()
    changes = {
        'title': 'Hi'
    }
    LinkService().update_link(link, changes)
    assert link.title == 'Hi'


def test_update_link_no_user_id_overwrite(scoped_app):
    """You should not be able to update the User ID
    for a link.
    """
    link = LinkFactory()
    NEW_USER_ID = 8
    ORIGINAL_USER_ID = link.user_id
    changes = {
        'title': 'Changing something',
        'user_id': NEW_USER_ID
    }
    LinkService().update_link(link, changes)
    assert link.user_id == ORIGINAL_USER_ID


def test_update_link_no_id_overwrite(scoped_app):
    """You should not be able to modify the ID for a link.
    """
    link = LinkFactory()
    NEW_ID = 42
    ORIGINAL_ID = link.id

    changes = {
        'id': NEW_ID
    }
    LinkService().update_link(link, changes)
    assert link.id == ORIGINAL_ID
