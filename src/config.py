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
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", default=db_string)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class CeleryConfig:
    broker_string = "pyamqp://{user}:{password}@localhost:5672//".format(
        user=os.getenv("RABBITMQ_DEFAULT_USER"),
        password=os.getenv("RABBITMQ_DEFAULT_PASS"),
    )
    broker_url = os.getenv("AMQP_URI", broker_string)
    timezone = "America/Toronto"
    enable_utc = True


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False


class TestConfig(Config):
    TESTING = True
    FLASK_APP = "src"
