# 🕷 Charlotte (API)

This is the backend that powers Charlotte, my personal link-saving tool for saving websites to read later, named after [a pretty awesome spider](https://en.wikipedia.org/wiki/Charlotte%27s_Web). It uses PostgreSQL to store URLs to read, and contains a REST API (built with Flask) that allows other applications to add/modify links easily (this allows me to add [Shortcuts](https://apps.apple.com/us/app/shortcuts/id915249334) actions to capture URLs quickly from any application with a share sheet, or create a send-to-email URL saving service).

## Table of Contents

* [Getting started](#-getting-started)
    * [Prerequisites](#prerequisites)
    * [Installing locally (Manual)](#installing-locally-manual)
    * [Installing locally with Docker Compose](#installing-locally-with-docker-compose)
    * [Deploying to Heroku](#deploying-to-heroku)
    * [Running unit tests](#running-unit-tests)
* [CLI Reference](#-cli-reference)
* [API Documentation](#-api-documentation)
    * [Authorization](#authorization)
    * [Getting user info: /api/user](#getting-user-info-apiuser)
        * [GET /api/user](#get-apiuser)
    * [Retrieving or adding links: /api/links](#retrieving-or-adding-links-apilinks)
        * [GET /api/links](#get-apilinks)
        * [POST /api/links](#post-apilinks)
    * [Retrieving, updating or deleting links: /api/links/:id](#retrieving-updating-or-deleting-links-apilinksid)
        * [GET /api/links/:id](#get-apilinksid)
        * [PATCH /api/links/:id](#patch-apilinksid)
        * [DELETE /api/links/:id](#delete-apilinksid)

## 🚀 Getting started

This will get you started on getting Charlotte installed locally to play with the API.

### Prerequisites

* A computer with Python 3.6+ installed
* Docker already installed and ready to go (or a local PostgreSQL instance if you're running without Docker)

Choose your adventure! 

* [Installing locally without Docker](#installing-locally-manual)
* [Installing locally with Docker Compose](#installing-locally-with-docker-compose)

### Installing locally (Manual)

1. Clone this repository in the directory of your choosing: `git clone https://github.com/mm/charlotte-api.git`

2. Set up and activate a virtual environment to keep dependencies for this project separate, then install requirements. For me on macOS it looks like this:

    ```console
    $ cd charlotte-api
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    ```

3. Create a `.env` file in the project's root directory with the following contents:

    ```
    FLASK_ENV=development
    DATABASE_URL="YOUR_DATABASE_CONNECTION_STRING"
    ```

    The `DATABASE_URL` environment variable needs to be a connection string to your local PostgreSQL database. It follows the form `postgresql://username:password@server/database`. Consult the [SQLAlchemy docs](https://docs.sqlalchemy.org/en/13/core/engines.html) for more info.

4. Use the CLI to initialize the database and create a new user/API key (make note of this key as we'll be making requests with it soon!):

    ```console
    $ flask admin create_db
    $ flask admin create_user
    ```

5. Start up the API with the built-in Flask development server: `flask run`.

### Installing locally (with Docker Compose)

1. Clone this repository in the directory of your choosing: `git clone https://github.com/mm/charlotte-api.git`

2. Ensure [Docker](https://www.docker.com/) is running (and Docker Compose [is installed](https://docs.docker.com/compose/install/))

3. Make a copy of the `dev/environment.example` file as `dev/environment`:

    ```console
    $ cp dev/environment.example dev/environment
    ```

4. Update environment variables in `dev/environment`: Update `an_insecure_password` to something a little more randomly generated. This will allow you to connect to the DB locally if you're interested in how it updates.

5. Build and run Charlotte! `docker-compose up --build`

6. Once everything's up and running, use the CLI to initialize the database and create a new user/API key (make note of this key as we'll be making requests with it soon!):

    ```console
    $ docker-compose run web flask admin create_db
    $ docker-compose run web flask admin create_user
    ```

7. You should be able to access the API at `http://127.0.0.1:8000`. Once you're done, stop any running containers with `docker-compose down`. 

8. When running in the future, you don't need to re-initialize the database, simply run `docker-compose up` in the project directory and you're ready to go!

### Deploying to Heroku

I deploy Charlotte to Heroku for my own use. Here's how it can be done:

1. Sign up for Heroku if you haven't already. Set up a new app and [provision the Heroku Postgres addon](https://devcenter.heroku.com/articles/heroku-postgresql#provisioning-heroku-postgres) for it. When you deploy this app to Heroku, the `DATABASE_URL` environment variable will be used automatically to give the correct URL for the Heroku Postgres instance (no need to copy it anywhere)

2. Ensure that the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) is installed.

3. If you haven't logged in to the CLI before, run `heroku login` first in your console. Then, add the Heroku remote to your repository and push to that remote:

    ```console
    $ heroku git:remote -a YOUR_APP_NAME_ON_HEROKU_HERE
    $ git push heroku master
    ```

4. If all goes well, you should now be able to initialize the database and create your API key remotely using the CLI!

    ```console
    $ heroku run flask admin create_db
    $ heroku run flask admin create_user
    ```

Enjoy :)

### Running unit tests

This application uses [pytest](https://docs.pytest.org/en/stable/) to run unit tests. Tests run against a SQLite database instead of a Postgres one. To run tests, at the project root start up pytest:

```console
$ pytest -v
```

## 🔑 CLI Reference

The CLI is where you can perform administrative functions on the application. From the project directory, you can run `flask admin <command name>` to run a command (or `docker compose run web flask admin <command name>`)

```console
$ flask admin
Usage: flask admin [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  create_db    Creates all database tables.
  create_user  Adds a new user to the database and generates an API key.
  drop_tables  Drops all database tables.
  rotate_key   Re-generates an API key.
```

## 📒 API Documentation

### Authorization

All API methods require you to authenticate with the API key generated by the CLI. The key must be passed in as an `x-api-key` HTTP header with every request. Failure to do so will yield a 403 error with this body:

```json
{
  "message": "Invalid API key. Please specify a key via the x-api-key header."
}
```

This was really only designed to be used for one person, but this scheme is definitely not ideal and rather basic as far as security goes. In the future I want to implement a 3rd party auth provider like [Auth0](https://auth0.com) (which would make authentication on the accompanying web app much easier too).

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

#### POST /api/links

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

    * **Location Header:** `http://localhost/api/links/30`

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

### Retrieving, updating or deleting links: /api/links/:id

Allows manipulation or retrieval of a given link stored in the database. If the link at the ID specified is not owned by the current user, a `403 Forbidden` is returned. 

* **URL**: `/api/links/:id`
* **Required**: `:id [integer]`
* **Method**: `GET, PATCH, DELETE`

#### GET /api/links/:id

Retrieves a link from the database with a given ID, or returns a `404` if the link wasn't found.

* **Example successful response:**

    `GET /api/links/30`

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

#### PATCH /api/links/:id

Updates a field in the database for a link with a given ID. Returns a `404` if the link wasn't found to begin with, or `422` if new data failed validation. Only fields passed in to the request body are updated.

* **Request Body**: JSON describing the fields to be changed and the new values. Keys can be any (or a combination) of `title, url, read` to change the URL's title, URL or read status (true/false) respectively.

* **Example successful request**:

    `PATCH /api/links/30`

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

#### DELETE /api/links/:id

Deletes an entry in the database for a link with a given ID. Returns a `404` if the link wasn't found. 

* **Example successful response**:

    `DELETE /api/links/30`

    **Code:** `200`

    **Response body:**

    ```json
    {
        "message": "Link with ID 30 deleted successfully"
    }
    ```












