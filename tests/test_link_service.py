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