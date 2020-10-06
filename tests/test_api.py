"""Tests on all Charlotte API routes."""

import pytest

from charlotte.model import db, Link

VALID_API_KEY = '204764892964d5931312b50f280a0112286f4ebb07111a65f7a1cb238437322d'

@pytest.mark.parametrize(('url', 'key', 'status_code'), (
    ('/api/user', '', 403),
    ('/api/links', '', 403),
    ('/api/links/1', '', 403),
    ('/api/user', VALID_API_KEY, 200),
    ('/api/links', VALID_API_KEY, 200),
    ('/api/links/1', VALID_API_KEY, 200)
))
def test_protected_endpoints(client, url, key, status_code):
    """The API key grants access to any method allowed on any resource. If the
    key is incorrect, any resource should return a 403 error on accession.
    """
    rv = client.get(url, headers={'x-api-key': key})
    assert rv.status_code == status_code


def test_user(client):
    """When /user is accessed, the current user for the provided API key should
    be outputted with the number of links, ID and name.
    """
    rv = client.get('/api/user', headers={'x-api-key': VALID_API_KEY})
    json_data = rv.get_json()
    assert rv.status_code == 200
    # On set-up the user should have 6 links (check `seed_link.sql`)
    assert json_data == {'id': 1, 'links': 6, 'name': 'Tester'}


@pytest.mark.parametrize('url', [
    '/api/links?page=a&per_page=b',
    '/api/links?page=1&per_page=a',
    '/api/links?page=a&per_page=1'
])
def test_invalid_pagination_for_links(client, url):
    """If a user accidentally puts a non-integer into the page or
    per_page parameters, warn them about that.
    """
    rv = client.get(url, headers={'x-api-key': VALID_API_KEY})
    json_data = rv.get_json()
    assert json_data['message'] == "The page and per_page parameters must be integers"


def test_links_response(client):
    """A request to /links should give back the list of links, but
    also pagination info and total links.
    """
    rv = client.get('/api/links', headers={'x-api-key': VALID_API_KEY})
    json_data = rv.get_json()
    assert len(json_data['links']) == 6
    assert json_data['next_page'] is None
    assert json_data['per_page'] == 20
    assert json_data['page'] == 1
    assert json_data['total_links'] == len(json_data['links'])
    assert json_data['total_pages'] == 1


@pytest.mark.parametrize(('url', 'page', 'per_page', 'next_page', 'total_pages'), (
    ('/api/links?page=1', 1, 20, None, 1),
    ('/api/links?page=1&per_page=4', 1, 4, 2, 2),
    ('/api/links?page=2&per_page=4', 2, 4, None, 2)
))
def test_pagination(client, url, page, per_page, next_page, total_pages):
    """Paginating on the /links endpoint should give appropriate
    pagination info depending on what was passed in via URL parameters.
    """
    rv = client.get(url, headers={'x-api-key': VALID_API_KEY})
    json_data = rv.get_json()
    assert json_data['page'] == page
    assert json_data['per_page'] == per_page
    assert json_data['next_page'] == next_page
    assert json_data['total_pages'] == total_pages


def test_link_get(client):
    """GETing a link directly from /api/links/<int> should return a JSON
    response containing the date added, ID, read status, title and URL.
    """
    rv = client.get('/api/links/2', headers={'x-api-key': VALID_API_KEY})
    json_data = rv.get_json()
    expected_response = {
        "date_added": "2020-08-02 09:30", 
        "id": 2, 
        "read": False, 
        "title": "PostgreSQL: Documentation", 
        "url": "https://www.postgresql.org/docs/"
    }
    assert json_data == expected_response


def test_link_post(client):
    """POSTing a link to /api/links should return a 201 - Created status code. The
    Location HTTP header should correspond to the link where you can access the new resource.
    """
    body = {
        'title': 'Netflix',
        'url': 'https://www.netflix.com'
    }
    rv = client.post('/api/links', headers={'x-api-key': VALID_API_KEY}, json=body)
    json_data = rv.get_json()
    new_id = json_data['id']
    assert rv.status_code == 201
    assert rv.headers['Location'] == 'http://localhost/api/links/'+str(new_id)


@pytest.mark.parametrize(('url', 'title'), (
    ('https://www.microsoft.com/en-ca/', 'Microsoft - Official Home Page'),
    ('https://github.com', 'GitHub: Where the world builds software · GitHub')
))
def test_link_post_infer_title(client, url, title):
    """POSTing a link without a title should cause the title of the URL to be
    inferred.
    """
    rv = client.post('/api/links', headers={'x-api-key': VALID_API_KEY}, json={'url': url})
    json_data = rv.get_json()
    assert rv.status_code == 201
    assert json_data['title'] == title


@pytest.mark.parametrize(('payload', 'status_code', 'validation_error'), (
    ({}, 422, 'Field may not be null.'),
    ({'url': 'frifh123'}, 422, 'Not a valid URL.'),
    ({'url': 'google'}, 422, 'Not a valid URL.'),
    ({'url': 'google.com'}, 422, 'Not a valid URL.')
))
def test_link_post_invalid_url(client, payload, status_code, validation_error):
    """POSTing an empty JSON payload, or an invalid URL should yield a 422, and
    a descriptive validation error in issues.url.
    """
    rv = client.post('/api/links', headers={'x-api-key': VALID_API_KEY}, json=payload)
    json_data = rv.get_json()

    assert rv.status_code == status_code
    print(json_data['issues'])
    assert validation_error in json_data['issues']['url']


@pytest.mark.parametrize(('url', 'status_code', 'message'), (
    ('/api/links/6', 200, 'Link with ID 6 deleted successfully'),
    ('/api/links/100', 404, 'Requested resource was not found in the database')
))
def test_link_delete(client, url, status_code, message):
    """Sending a DELETE request to /api/links/<int:id> should return a 200 if successful,
    and a message notifying the user that it was successful (or a 404 if not found)
    """
    rv = client.delete(url, headers={'x-api-key': VALID_API_KEY})
    assert rv.status_code == status_code
    assert rv.get_json().get('message') == message


@pytest.mark.parametrize(('id', 'payload', 'status_code', 'message'), (
    (1, {'read': True}, 200, 'Link with ID 1 updated successfully'),
    (2, {'read': True, 'title': 'Updated title'}, 200, 'Link with ID 2 updated successfully'),
    (2, None, 400, 'This method expects valid JSON data as the request body'),
    (2, {}, 200, 'Link with ID 2 updated successfully'),
    (7, {'read': True}, 404, 'Requested resource was not found in the database'),
    (3, {'url': 'hryufhryf'}, 422, 'The submitted data failed validation checks'),
    (3, {'url': None}, 422, 'The submitted data failed validation checks')
))
def test_link_patch(app, client, id, payload, status_code, message):
    """Sending a PATCH request with a valid body and on a valid link should
    return a 200 if successful, and a message notifying the user that it was successful.
    An empty JSON payload should still yield a 200 (nothing was changed)
    """
    rv = client.patch('/api/links/'+str(id), headers={'x-api-key': VALID_API_KEY}, json=payload)

    assert rv.status_code == status_code
    assert rv.get_json().get('message') == message

    # Check whether our underlying object is actually updated (if we sent something valid)
    if rv.status_code == 200:
        with app.app_context():
            updated_link = Link.query.get(id)
            for key, value in payload.items():
                assert getattr(updated_link, key) == value
