import os
import tempfile
import pytest

from untitled import create_app
from untitled.model import db

VALID_API_KEY = '189f8f7b42944ba7bca361666c9fdded'

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
    assert json_data == {'id': 1, 'links': 1, 'name': 'Tester'}

