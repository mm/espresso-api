"""Handles setting up Flask configuration variables depending on the environment
Charlotte is running in.
"""

import os
from dotenv import find_dotenv, load_dotenv


class Config(object):
    """Base configuration all other configurations inherit from."""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False


class TestConfig(Config):
    TESTING = True
    FLASK_APP = 'charlotte'
