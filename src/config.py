"""Handles setting up Flask configuration variables depending on the environment
Espresso is running in.
"""

import os


class Config:
    """Base configuration all other configurations inherit from."""

    db_string = "postgresql://{user}:{password}@{host}/{db}".format(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        db=os.getenv("DB_DATABASE"),
    )

    # Try to find a DATABASE_URL environment variable. If none is found,
    # fall back to one assembled from DB_USER, _PASSWORD, _HOST and _DATABASE
    # env vars:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", default=db_string).replace("postgres", "postgresql")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if os.getenv("REDIS_BASE_URL"):
        RATELIMIT_STORAGE_URL = os.getenv("REDIS_BASE_URL") + "/1"
    else:
        RATELIMIT_STORAGE_URL = "memory://"


class CeleryConfig:
    if os.getenv("REDIS_BASE_URL"):
        broker_string = os.getenv("REDIS_BASE_URL") + "/1"
    else:
        broker_string = "redis://localhost:6379/0"
    broker_url = os.getenv("BROKER_URL", broker_string)
    timezone = "America/Toronto"
    enable_utc = True


class DevConfig(Config):
    DEBUG = True
    RATELIMIT_ENABLED = False


class ProdConfig(Config):
    DEBUG = False


class TestConfig(Config):
    TESTING = True
    FLASK_APP = "src"
    RATELIMIT_ENABLED = False
