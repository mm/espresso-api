import pytest
from src.model import Link, LinkSchema
from .factories import LinkFactory


def test_no_api_key_should_401(scoped_client):
    rv = scoped_client.get("/v1/links")
    assert rv.status_code == 401


@pytest.mark.parametrize(
    "url",
    [
        "/v1/links?page=a&per_page=b",
        "/v1/links?page=1&per_page=a",
        "/v1/links?page=a&per_page=1",
    ],
)
def test_invalid_pagination_for_links(scoped_client, test_user, url: str):
    """If a user accidentally puts a non-integer into the page or
    per_page parameters, warn them about that.
    """
    user, api_key = test_user

    rv = scoped_client.get(url, headers={"x-api-key": api_key})
    json_data = rv.get_json()
    assert json_data["message"] == "The submitted data failed validation checks"


def test_links_response(scoped_client, test_user):
    """A request to /links should give back the list of links, but
    also pagination info and total links.
    """
    user, api_key = test_user
    rv = scoped_client.get("/v1/links", headers={"x-api-key": api_key})
    json_data = rv.get_json()
    assert "next_page" in json_data
    assert "per_page" in json_data
    assert "page" in json_data
    assert "total_pages" in json_data


@pytest.mark.parametrize(
    ("url", "read_filter"),
    (
        ("/v1/links?show=all", "all"),
        ("/v1/links", "all"),
        ("/v1/links?show=read", "read"),
        ("/v1/links?show=unread", "unread"),
    ),
)
def test_show_switch(scoped_client, test_user, url, read_filter):
    """The `show` parameter should control whether unread (default), read or all
    links are shown.
    """
    user, api_key = test_user
    LinkFactory.create_batch(20, user=user)
    rv = scoped_client.get(url, headers={"x-api-key": api_key})
    json_data = rv.get_json()
    read_statuses = [link["read"] for link in json_data["links"]]
    # If we passed in 'read' as the filter, all read statuses for the links should be True
    if read_filter == "read":
        assert all((x == True for x in read_statuses))
    # If we passed in 'unread' as the filter, all read statuses for the links should be False
    elif read_filter == "unread":
        assert all((not x for x in read_statuses))
    # Otherwise, it doesn't matter as long as the status is a boolean:
    else:
        assert all((type(x) == bool for x in read_statuses))


def test_link_get(scoped_app, scoped_client, test_user):
    """GETing a link directly from /api/links/<int> should return a JSON
    response containing the date added, ID, read status, title and URL.
    """
    user, api_key = test_user
    link = LinkFactory(user=user)
    rv = scoped_client.get(f"/v1/links/{link.id}", headers={"x-api-key": api_key})
    json_data = rv.get_json()
    with scoped_app.app_context():
        link = Link.query.get(link.id)
        assert LinkSchema().dump(link) == json_data


def test_link_post(scoped_client, test_user):
    """POSTing a link to /api/links should return a 201 - Created status code. The
    Location HTTP header should correspond to the link where you can access the new resource.
    """
    user, api_key = test_user
    body = {"title": "Netflix", "url": "https://www.netflix.com"}
    rv = scoped_client.post("/v1/links", headers={"x-api-key": api_key}, json=body)
    json_data = rv.get_json()
    print(json_data)
    new_id = json_data["id"]
    assert rv.status_code == 201
    assert rv.headers["Location"] == "http://localhost/v1/links/" + str(new_id)


@pytest.mark.parametrize(
    ("payload", "status_code", "validation_error"),
    (
        ({}, 422, "Missing data for required field."),
        ({"url": "frifh123"}, 422, "Not a valid URL."),
        ({"url": "google"}, 422, "Not a valid URL."),
        ({"url": "google.com"}, 422, "Not a valid URL."),
    ),
)
def test_link_post_invalid_url(
    scoped_client, test_user, payload, status_code, validation_error
):
    """POSTing an empty JSON payload, or an invalid URL should yield a 422, and
    a descriptive validation error in issues.url.
    """
    user, api_key = test_user
    rv = scoped_client.post("/v1/links", headers={"x-api-key": api_key}, json=payload)
    json_data = rv.get_json()

    assert rv.status_code == status_code
    print(json_data["issues"])
    assert validation_error in json_data["issues"]["url"]


def test_link_delete(scoped_client, test_user):
    """Sending a DELETE request to /api/links/<int:id> should return a 200 if successful,
    and a message notifying the user that it was successful.
    """
    user, api_key = test_user
    link = LinkFactory(user=user)
    rv = scoped_client.delete(f"/v1/links/{link.id}", headers={"x-api-key": api_key})
    assert rv.status_code == 200
    assert (
        rv.get_json().get("message") == f"Link with ID {link.id} deleted successfully"
    )


@pytest.mark.parametrize(
    ("payload", "status_code", "message"),
    (
        ({"read": True}, 200, "Link with ID {} updated successfully"),
        (
            {"read": True, "title": "Updated title"},
            200,
            "Link with ID {} updated successfully",
        ),
        (None, 422, "The submitted data failed validation checks"),
        ({}, 200, "Link with ID {} updated successfully"),
        ({"url": "hryufhryf"}, 422, "The submitted data failed validation checks"),
        ({"url": None}, 422, "The submitted data failed validation checks"),
    ),
)
def test_link_patch(
    scoped_app, scoped_client, test_user, payload, status_code, message
):
    """Sending a PATCH request with a valid body and on a valid link should
    return a 200 if successful, and a message notifying the user that it was successful.
    An empty JSON payload should still yield a 200 (nothing was changed)
    """
    user, api_key = test_user
    link = LinkFactory(user=user)
    rv = scoped_client.patch(
        f"/v1/links/{link.id}", headers={"x-api-key": api_key}, json=payload
    )

    assert rv.status_code == status_code
    assert rv.get_json().get("message") == message.format(link.id)

    # Check whether our underlying object is actually updated (if we sent something valid)
    if rv.status_code == 200:
        with scoped_app.app_context():
            updated_link = Link.query.get(link.id)
            for key, value in payload.items():
                assert getattr(updated_link, key) == value
