# Charlotte (API)

This is the back-end that powers Charlotte, my personal link-saving tool for saving websites to read later. It uses PostgreSQL to store URLs to read, and contains a REST API (built with Flask) that allows other applications to add/modify links easily (this allows me to add [Shortcuts](https://apps.apple.com/us/app/shortcuts/id915249334) actions to capture URLs quickly from any application with a share sheet, or create a send-to-email URL saving service).

## Getting started

This will get you started on getting Charlotte installed locally to play with the API.

### Prerequisites

* A computer with Python 3.6+ installed
* Docker already installed and ready to go

### Installing

1. Clone this repository in the directory of your choosing: `git clone https://github.com/mm/charlotte-api.git`

2. Set up and activate a virtual environment to keep dependencies for this project separate, then install requirements. For me on macOS it looks like this:

    ```console
    cd charlotte-api
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the project's root directory with the following contents:

    ```
    FLASK_ENV=development
    DATABASE_URL="YOUR_DATABASE_CONNECTION_STRING"
    ```

    The `DATABASE_URL` environment variable needs to be a connection string to your local PostgreSQL database. It follows the form `postgresql://username:password@server/database`. Consult the [SQLAlchemy docs](https://docs.sqlalchemy.org/en/13/core/engines.html) for more info.

4. Use the CLI to initialize the database and create a new user/API key (make note of this key as we'll be making requests with it soon!):

    ```console
    flask admin create_db
    flask admin create_user
    ```

5. Start up the API with the built-in Flask development server: `flask run`.

## API Documentation

### Authorization

All API methods require you to authenticate with the API key generated by the CLI. The key must be passed in as an `x-api-key` HTTP header with every request. Failure to do so will yield a 403 error with this body:

```json
{
  "message": "Invalid API key. Please specify a key via the x-api-key header."
}
```

This is definitely not ideal and rather basic as far as security goes. In the future I want to implement a 3rd party auth provider like [Auth0](https://auth0.com) (which would make authentication on the accompanying web app much easier too).

### Getting user info: /api/user

Returns information about the current user (detected via API key).

* **URL**: `/api/user`
* **Method**: `GET`

#### GET /api/user:

* **Example successful response:**

    * **Code**: `200`
    * **Response body**:

        ```json
        {
            "id": 1, 
            "links": 7, 
            "name": "Matt"
        }
        ```

### Retrieving or adding links: /api/links

* **URL**: `/api/links`
* **Method**: `GET, POST`

#### GET /api/links

Returns a list of links belonging to the current user. By default, this will paginate to show 20 links per page, sorted in order of most recently added links first.

* **URL Parameters:**

    * `per_page=[integer]`: The number of links to show per page (default 20)
    * `page=[integer]`: The page number of links to retrieve (will yield a 404 if out of bounds)

* **Example successful response:**

    * **Code**: 200
    * **Response body:**

        ```json
        {
            "links": [
                {
                    "date_added": "2020-08-03 02:52 PM ", 
                    "id": 28, 
                    "read": false, 
                    "title": "Tutorial: VPN on Demand with Siri, Shortcuts, Python, AWS EC2 & Lambda - DEV", 
                    "url": "https://dev.to/mmascioni/tutorial-vpn-on-demand-with-siri-shortcuts-python-aws-ec2-lambda-i83"
                }
            ], 
            "next_page": null, 
            "page": 1, 
            "per_page": 20, 
            "total_links": 1, 
            "total_pages": 1
        }
        ```

#### POST /api/links

Adds a new link to the database. If a title wasn't provided, the backend attempts to infer one from the `<title>` element of the URL passed in. A JSON representation of the link will be returned in the response, with a `201` code if successful.

* **Request body**: Must be valid JSON of this form:

    ```json
    {
        "title": "Apple",
        "url": "https://apple.com"
    }
    ```

    Note that only `url` is required. If `title` wasn't passed in, the title is inferred from the site's `<title>` element.

* **Example successful response:**:

    * **Code:** 201
    * **Response body:**

        ```json
        {
            "date_added": "2020-08-15 10:31 PM ", 
            "id": 30, 
            "read": false, 
            "title": "Apple", 
            "url": "https://apple.com"
        }
        ```
        Note that `date_added` is in UTC.

    * **Location Header:** `http://localhost/api/links/30`

* **Example validation error:**:

    Returned if, for example, the URL is invalid.

    * **Code:** 422
    * **Response body:**

        ```json
        {
            "issues": {
                "url": [
                    "Not a valid URL."
                ]
            }, 
            "message": "The submitted data failed validation checks"
        }
        ```

### Retrieving, updating or deleting links: /api/links/:id

Allows manipulation or retrieval of a given link stored in the database. If the link at the ID specified is not owned by the current user, a `403 Forbidden` is returned. 

* **URL**: `/api/links/:id`
* **Required**: `:id (integer)`
* **Method**: `GET, PATCH, DELETE`

#### GET /api/links/:id

Retrieves a link from the database with a given ID, or returns a `404` if the link wasn't found.

* **Example successful response:**

    `GET /api/links/30`

    **Code**: 200

    **Response body**:

        ```json
        {
            "date_added": "2020-08-15 10:31 PM ", 
            "id": 30, 
            "read": false, 
            "title": "Apple", 
            "url": "https://apple.com"
        }
        ```
        Note that `date_added` is in UTC.

#### PATCH /api/links/:id

Updates a field in the database for a link with a given ID. Returns a `404` if the link wasn't found to begin with, or `422` if new data failed validation. Only fields passed in to the request body are updated.

* **Request Body**: JSON describing the fields to be changed and the new values. Keys can be any (or a combination) of `title, url, read` to change the URL's title, URL or read status (true/false) respectively.

* **Example successful request**:

    `PATCH /api/links/30`

    **Request body:**

    ```json
    {"read": true }
    ```

    **Code:** 200
    **Response body:**

    ```json
    {
        "message": "Link with ID 30 updated successfully"
    }
    ```

#### DELETE /api/links/:id

Deletes an entry in the database for a link with a given ID. Returns a `404` if the link wasn't found. 

* **Example successful response**:

    `DELETE /api/links/30`

    **Code:** 200
    **Response body:**

    ```json
    {
        "message": "Link with ID 30 deleted successfully"
    }
    ```












