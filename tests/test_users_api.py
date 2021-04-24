import pytest
from src.model import Link, LinkSchema
from src.auth.service import AuthService
from .factories import LinkFactory, UserFactory


def test_get_user_no_api_key_should_401(scoped_client):
    rv = scoped_client.get("/v1/auth/user")
    assert rv.status_code == 401


def test_get_user(scoped_client, test_user):
    user, api_key = test_user
    rv = scoped_client.get("/v1/auth/user", headers={"x-api-key": api_key})
    json_data = rv.get_json()
    assert rv.status_code == 200
    assert json_data["id"] == user.id
    assert "links" in json_data
    assert json_data["name"] == user.name
