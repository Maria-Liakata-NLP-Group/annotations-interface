import os
import ast

basedir = os.path.abspath(os.path.dirname(__file__))


def get_app_admin(admin_emails):
    """Return app admin email(s) as a list"""
    return ast.literal_eval(admin_emails)


class BaseConfig(object):
    """Base configuration. Configuration settings are defined here."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, "data")  # folder for uploaded files
    APP_ADMIN = os.environ.get("APP_ADMIN")  # admin email(s), specified in .flaskenv
    if APP_ADMIN:
        # convert string to list if APP_ADMIN environment variable is set
        APP_ADMIN = get_app_admin(APP_ADMIN)


class TestConfig(BaseConfig):
    """Test configuration. Configuration settings are defined here."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # in-memory database
    WTF_CSRF_ENABLED = False  # disable CSRF tokens in the Forms
    APP_ADMIN = get_app_admin("['admin1@example.com', 'admin2@example.com']")
