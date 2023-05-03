import os


class BaseConfig(object):
    """Base configuration. Configuration settings are defined here."""
    SECRET_KEY = os.environ["FLASK_APP_SECRET_KEY"]
