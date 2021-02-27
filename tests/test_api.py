"""Tests on all Charlotte API routes."""

from datetime import datetime
import pytest
from src.model import db, Link, LinkSchema

link_schema = LinkSchema()

def test_user(client, seed_data):
    """When /user is accessed, the current user for the provided API key should
    be outputted with the number of links, ID and name.
    """
    user_id, api_key = seed_data
    rv = client.get('/v1/auth/user', headers={'x-api-key': api_key})
    json_data = rv.get_json()
    assert rv.status_code == 200
    assert 'id' in json_data
    assert 'links' in json_data
    assert 'name' in json_data


@pytest.mark.parametrize('url', [
    '/v1/links?page=a&per_page=b',
    '/v1/links?page=1&per_page=a',
    '/v1/links?page=a&per_page=1'
])
def test_invalid_pagination_for_links(client, seed_data, url):
    """If a user accidentally puts a non-integer into the page or
    per_page parameters, warn them about that.
    """
    user_id, api_key = seed_data
    rv = client.get(url, headers={'x-api-key': api_key})
    json_data = rv.get_json()
    assert json_data['message'] == "The page and per_page parameters must be integers"


# TODO: Expand this to test out pagination better, without being dependent on seed amounts:
def test_links_response(client, seed_data):
    """A request to /links should give back the list of links, but
    also pagination info and total links.
    """
    user_id, api_key = seed_data
    rv = client.get('/v1/links', headers={'x-api-key': api_key})
    json_data = rv.get_json()
    assert 'next_page' in json_data
    assert 'per_page' in json_data
    assert 'page' in json_data
    assert 'total_pages' in json_data


@pytest.mark.parametrize(('url', 'read_filter'), (
    ('/v1/links?show=all', 'all'),
    ('/v1/links', 'all'),
    ('/v1/links?show=read', 'read'),
    ('/v1/links?show=unread', 'unread')
))
def test_show_switch(client, seed_data, url, read_filter):
    """The `show` parameter should control whether unread (default), read or all
    links are shown.
    """
    user_id, api_key = seed_data
    rv = client.get(url, headers={'x-api-key': api_key})
    json_data = rv.get_json()
    read_statuses = [link['read'] for link in json_data['links']]
    # If we passed in 'read' as the filter, all read statuses for the links should be True
    if read_filter == 'read':
        assert all((x == True for x in read_statuses))
    # If we passed in 'unread' as the filter, all read statuses for the links should be False
    elif read_filter == 'unread':
        assert all((not x for x in read_statuses))
    # Otherwise, it doesn't matter as long as the status is a boolean:
    else:
        assert all((type(x) == bool for x in read_statuses))


def test_link_get(client, app, seed_data):
    """GETing a link directly from /api/links/<int> should return a JSON
    response containing the date added, ID, read status, title and URL.
    """
    user_id, api_key = seed_data
    rv = client.get('/v1/links/2', headers={'x-api-key': api_key})
    json_data = rv.get_json()
    with app.app_context():
        link = Link.query.get(2)
        assert link_schema.dump(link) == json_data


def test_link_post(client, seed_data):
    """POSTing a link to /api/links should return a 201 - Created status code. The
    Location HTTP header should correspond to the link where you can access the new resource.
    """
    user_id, api_key = seed_data
    body = {
        'title': 'Netflix',
        'url': 'https://www.netflix.com'
    }
    rv = client.post('/v1/links', headers={'x-api-key': api_key}, json=body)
    json_data = rv.get_json()
    new_id = json_data['id']
    assert rv.status_code == 201
    assert rv.headers['Location'] == 'http://localhost/v1/links/'+str(new_id)


@pytest.mark.parametrize(('url', 'title'), (
    ('https://www.microsoft.com/en-ca/', 'Microsoft - Official Home Page'),
    ('https://github.com', 'GitHub: Where the world builds software · GitHub')
))
def test_link_post_infer_title(client, seed_data, url, title):
    """POSTing a link without a title should cause the title of the URL to be
    inferred.
    """
    user_id, api_key = seed_data
    rv = client.post('/v1/links', headers={'x-api-key': api_key}, json={'url': url})
    json_data = rv.get_json()
    assert rv.status_code == 201
    assert json_data['title'] == title


@pytest.mark.parametrize(('payload', 'status_code', 'validation_error'), (
    ({}, 422, 'Field may not be null.'),
    ({'url': 'frifh123'}, 422, 'Not a valid URL.'),
    ({'url': 'google'}, 422, 'Not a valid URL.'),
    ({'url': 'google.com'}, 422, 'Not a valid URL.')
))
def test_link_post_invalid_url(client, seed_data, payload, status_code, validation_error):
    """POSTing an empty JSON payload, or an invalid URL should yield a 422, and
    a descriptive validation error in issues.url.
    """
    user_id, api_key = seed_data
    rv = client.post('/v1/links', headers={'x-api-key': api_key}, json=payload)
    json_data = rv.get_json()

    assert rv.status_code == status_code
    print(json_data['issues'])
    assert validation_error in json_data['issues']['url']


@pytest.mark.parametrize(('url', 'status_code', 'message'), (
    ('/v1/links/6', 200, 'Link with ID 6 deleted successfully'),
    ('/v1/links/100', 404, 'Requested resource was not found')
))
def test_link_delete(client, seed_data, url, status_code, message):
    """Sending a DELETE request to /api/links/<int:id> should return a 200 if successful,
    and a message notifying the user that it was successful (or a 404 if not found)
    """
    user_id, api_key = seed_data
    rv = client.delete(url, headers={'x-api-key': api_key})
    assert rv.status_code == status_code
    assert rv.get_json().get('message') == message


@pytest.mark.parametrize(('id', 'payload', 'status_code', 'message'), (
    (1, {'read': True}, 200, 'Link with ID 1 updated successfully'),
    (2, {'read': True, 'title': 'Updated title'}, 200, 'Link with ID 2 updated successfully'),
    (2, None, 400, 'This method expects valid JSON data as the request body'),
    (2, {}, 200, 'Link with ID 2 updated successfully'),
    (150, {'read': True}, 404, 'Requested resource was not found'),
    (3, {'url': 'hryufhryf'}, 422, 'The submitted data failed validation checks'),
    (3, {'url': None}, 422, 'The submitted data failed validation checks')
))
def test_link_patch(app, client, seed_data, id, payload, status_code, message):
    """Sending a PATCH request with a valid body and on a valid link should
    return a 200 if successful, and a message notifying the user that it was successful.
    An empty JSON payload should still yield a 200 (nothing was changed)
    """
    user_id, api_key = seed_data
    rv = client.patch('/v1/links/'+str(id), headers={'x-api-key': api_key}, json=payload)

    assert rv.status_code == status_code
    assert rv.get_json().get('message') == message

    # Check whether our underlying object is actually updated (if we sent something valid)
    if rv.status_code == 200:
        with app.app_context():
            updated_link = Link.query.get(id)
            for key, value in payload.items():
                assert getattr(updated_link, key) == value
