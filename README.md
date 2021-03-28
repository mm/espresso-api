# ☕️ Espresso (API)

This is the backend that powers Espresso, my personal link-saving tool for saving websites to read later. It uses PostgreSQL to store URLs to read, and contains a REST API (built with Flask) that allows other applications to add/modify links easily (this allows me to add [Shortcuts](https://apps.apple.com/us/app/shortcuts/id915249334) actions to capture URLs quickly from any application with a share sheet, or create a send-to-email URL saving service).

----
🚧 **Under Construction**: Espresso is still being developed. Hoping to release it as a self-hosted link saving tool!

----

## Table of Contents

* [Getting started](#-getting-started)
    * [Prerequisites](#prerequisites)
    * [Installing with Docker Compose](#installing-locally-with-docker-compose)
    * [Installing without Docker](#installing-locally-manual)
    * [Deploying to Heroku](#deploying-to-heroku)
    * [Running unit tests](#running-unit-tests)
* [CLI Reference](#-cli-reference)
* [API Documentation](#-api-documentation)
    * [Authorization](#authorization)
    * [Getting user info: /auth/user](#getting-user-info-authuser)
        * [GET /auth/user](#get-authuser)
    * [Retrieving or adding links: /links](#retrieving-or-adding-links)
        * [GET /links](#get-links)
        * [POST /links](#post-links)
    * [Retrieving, updating or deleting links: /links/:id](#retrieving-updating-or-deleting-links-linksid)
        * [GET /links/:id](#get-linksid)
        * [PATCH /links/:id](#patch-linksid)
        * [DELETE /links/:id](#delete-linksid)

## 🚀 Getting started

This will get you started on getting Espresso installed locally to play with the API.

### Prerequisites

* A computer with Python 3.9+ installed
* Docker already installed and ready to go (or a local PostgreSQL instance if you're running without Docker)

Choose your adventure! 

* [Installing with Docker Compose](#installing-locally-with-docker-compose)
* [Installing without Docker](#installing-locally-manual)

### Installing locally (with Docker Compose)

1. Clone this repository in the directory of your choosing: `git clone https://github.com/mm/espresso-api.git`

2. Ensure [Docker](https://www.docker.com/) is running (and Docker Compose [is installed](https://docs.docker.com/compose/install/))

3. Make a copy of the `.env.example` file as `.env`, for example:

    ```console
    $ cp .env.example .env
    ```

4. Update environment variables in `.env` to your liking -- these control the PostgreSQL username, password and database. The `DB_HOST` variable isn't used in Docker Compose builds.

5. Build and run Espresso! `docker-compose up -d`

6. Upgrade the database structure to the latest version: `docker-compose run web flask db upgrade`

7. Once everything's up and running, you can use the CLI to generate a testing environment with a few links already populated for you. Make note of the API key it outputs as you can use this to access the API methods afterwards.

    ```console
    $ docker-compose run web flask admin dummy
    ```

8. You should be able to access the API at `http://127.0.0.1:8000`. Once you're done, stop any running containers with `docker-compose down`. 

### Installing locally (Manual)

1. Clone this repository in the directory of your choosing: `git clone https://github.com/mm/espresso-api.git`

2. Install dependencies with [Pipenv](https://pipenv.pypa.io/en/latest/):

    ```console
    $ cd espresso-api
    $ pipenv install
    ```

3. Copy the `.env.example` file into an `.env` file to store environment variables:

    ```console
    $ cp .env.example .env
    ```

    To specify how to get to your database, you can specify either a `DATABASE_URL` environment variable (see the [SQLAlchemy docs](https://docs.sqlalchemy.org/en/13/core/engines.html) for how this is formatted) or manually specify:

    - `DB_USER`
    - `DB_PASSWORD`
    - `DB_DATABASE`
    - `DB_HOST`

    If a `DATABASE_URL` variable *and* the above variables are specified, the `DATABASE_URL` takes precedence. Otherwise, a URL connection string is automatically generated.

4. Upgrade the database structure to the latest version: `flask db upgrade`

5. Use the CLI to generate test data for your environment (a testing user with some links). You can specify your name and email and it'll give you an API key to access the API with as well. Make note of the API key it outputs as you can use this to test out the API methods afterwards.

    ```console
    $ flask admin dummy --name Matt --email hello@example.com
    ```

6. Start up the API with the built-in Flask development server: `flask run`.

### Deploying to Heroku

I deploy Espresso to Heroku for my own use. Here's how it can be done:

1. Sign up for Heroku if you haven't already. Set up a new app and [provision the Heroku Postgres addon](https://devcenter.heroku.com/articles/heroku-postgresql#provisioning-heroku-postgres) for it. When you deploy this app to Heroku, the `DATABASE_URL` environment variable will be used automatically to give the correct URL for the Heroku Postgres instance (no need to copy it anywhere)

2. Ensure that the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) is installed.

3. If you haven't logged in to the CLI before, run `heroku login` first in your console. Then, add the Heroku remote to your repository and push to that remote:

    ```console
    $ heroku git:remote -a YOUR_APP_NAME_ON_HEROKU_HERE
    $ git push heroku master
    ```

4. If all goes well, you should now be able to initialize the database and create your API key remotely using the CLI!

    ```console
    $ heroku run flask db upgrade
    $ heroku run flask admin new_user --name Matt --email hello@example.com
    ```

Enjoy :)

### Running unit tests

This application uses [pytest](https://docs.pytest.org/en/stable/) to run unit tests. Tests run against a SQLite database instead of a Postgres one. To run tests, at the project root start up pytest:

```console
$ pytest -v
```

You can also run tests in a Docker container:

```console
$ docker-compose run --rm web pytest -v
```

## 🔑 CLI Reference

The CLI is where you can perform a couple administrative functions on the application. From the project directory, you can run `flask admin <command name>` to run a command (or `docker compose run web flask admin <command name>`)

```console
$ flask admin
Usage: flask admin [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  clear_tables  Deletes all data.
  drop_tables   Drops all database tables.
  dummy         Creates a dummy testing environment, complete with a test...
  new_user      Creates a new user with an API key.
```

## 📒 API Documentation

All API methods are prefixed with a `v1` (i.e. `/v1/links/4`)

### Authorization

All API methods require you to authenticate with the API key generated by the CLI. The key must be passed in as an `x-api-key` HTTP header with every request. Failure to do so will yield a 401 error with this body:

```json
{
  "message": "Authorization is required to access this resource."
}
```

This was really only designed to be used for one person, but this scheme is definitely not ideal and rather basic as far as security goes. In the future I want to implement a 3rd party auth provider like [Auth0](https://auth0.com) (which would make authentication on the accompanying web app much easier too).

### Getting user info: /auth/user

Returns information about the current user (detected via API key).

* **URL**: `/auth/user`
* **Method**: `GET`

#### GET /auth/user:

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

### Retrieving or adding links: /links

* **URL**: `/links`
* **Method**: `GET, POST`

#### GET /links

Returns a list of links belonging to the current user. By default, this will paginate to show 20 links per page, sorted in order of most recently added links first.

* **URL Parameters:**

    * `per_page=[integer]`: The number of links to show per page (default 20)
    * `page=[integer]`: The page number of links to retrieve (will yield a 404 if out of bounds)
    * `show=[string{all, read, unread}]`: Controls whether unread, read or all links are returned:
        * `unread` (Default): Returns only links which haven't been marked as read yet
        * `read`: Returns only links which have been marked as read
        * `all`: Returns all links regardless of read status

* **Example successful response:**

    * **Code**: `200`
    * **Response body:**

        ```json
        {
            "links": [
                {
                    "date_added": "2020-08-03 14:52", 
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

* Note that `total_links` will always reflect the total number of links the user has saved, regardless of the value passed to the `show` parameter.

#### POST /links

Adds a new link to the database. If a title wasn't provided, the backend attempts to infer one from the `<title>` element of the URL passed in. A JSON representation of the link will be returned in the response, with a `201` code if successful. URLs need to have a scheme specified as well as a TLD.

* **Request body**: Must be valid JSON of this form:

    ```json
    {
        "title": "Apple",
        "url": "https://apple.com"
    }
    ```

    Note that only `url` is required. If `title` wasn't passed in, the title is inferred from the site's `<title>` element.

* **Example successful response:**:

    * **Code:** `201`
    * **Response body:**

        ```json
        {
            "date_added": "2020-08-15 22:31", 
            "id": 30, 
            "read": false, 
            "title": "Apple", 
            "url": "https://apple.com"
        }
        ```
        Note that `date_added` is in UTC.

    * **Location Header:** `http://localhost/links/30`

* **Example validation error:**:

    Returned if, for example, the URL is invalid.

    * **Code:** `422`
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

### Retrieving, updating or deleting links: /links/:id

Allows manipulation or retrieval of a given link stored in the database. If the link at the ID specified is not owned by the current user, a `403 Forbidden` is returned. 

* **URL**: `/links/:id`
* **Required**: `:id [integer]`
* **Method**: `GET, PATCH, DELETE`

#### GET /links/:id

Retrieves a link from the database with a given ID, or returns a `404` if the link wasn't found.

* **Example successful response:**

    `GET /links/30`

    **Code**: `200`

    **Response body**:

    ```json
    {
        "date_added": "2020-08-15 22:31", 
        "id": 30, 
        "read": false, 
        "title": "Apple", 
        "url": "https://apple.com"
    }
    ```
    Note that `date_added` is in UTC.

#### PATCH /links/:id

Updates a field in the database for a link with a given ID. Returns a `404` if the link wasn't found to begin with, or `422` if new data failed validation. Only fields passed in to the request body are updated.

* **Request Body**: JSON describing the fields to be changed and the new values. Keys can be any (or a combination) of `title, url, read` to change the URL's title, URL or read status (true/false) respectively.

* **Example successful request**:

    `PATCH /links/30`

    **Request body:**

    ```json
    {"read": true }
    ```

    **Code:** `200`
    
    **Response body:**

    ```json
    {
        "message": "Link with ID 30 updated successfully"
    }
    ```

#### DELETE /links/:id

Deletes an entry in the database for a link with a given ID. Returns a `404` if the link wasn't found. 

* **Example successful response**:

    `DELETE /links/30`

    **Code:** `200`

    **Response body:**

    ```json
    {
        "message": "Link with ID 30 deleted successfully"
    }
    ```












