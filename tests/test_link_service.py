from tests.factories import UserFactory, LinkFactory
from src.links.service import LinkService
from werkzeug.exceptions import NotFound
from unittest.mock import patch
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
        'title': 'Hi',
        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    }
    LinkService().update_link(link, changes)
    assert link.title == 'Hi'
    assert link.url == 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'


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
    assert link.title == 'Changing something'


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


def test_delete_link(scoped_app):
    link = LinkFactory()
    # Persist it to the database
    LinkService().create_link(link)
    link_id = int(link.id)
    # Delete it:
    LinkService().delete_link(link)

    # When you try accessing it again, NotFound should be raised:
    with pytest.raises(NotFound):
        LinkService().get_link(link_id)


@pytest.mark.parametrize("show_param", ['all', 'read', 'unread'])
def test_get_links_show_param(scoped_app, show_param):
    """The 'show' parameter should control whether all, only read or
    only unread links are shown in the API response.
    """
    # Create a user and 100 links beneath them:
    user = UserFactory()
    links = LinkFactory.build_batch(100, user=user)
    link_service = LinkService()

    params = {'page': 1, 'per_page': 50, 'show': show_param}

    response = link_service.get_many_links(user.id, params)
    read_statuses = [x.read for x in response['links']]
    if show_param == 'all':
        assert all((type(x) == bool for x in read_statuses))
    elif show_param == 'read':
        assert all((x == True for x in read_statuses))
    elif show_param == 'unread':
        assert all((x == False for x in read_statuses))


def test_create_link_without_title(scoped_app):
    """When creating a link without a title, the service should
    try to fetch the title from the website's HTML
    """

    with patch('src.helpers.requests') as mock_requests:
        mock_requests.get.return_value.text = '<title>Never Gonna</title>'

        link = LinkFactory(title=None)
        LinkService().create_link(link)
        assert link.title == 'Never Gonna'
