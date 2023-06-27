from flask import Flask
from config import BaseConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy import MetaData

# custom metadata naming convention
# this is required for dealing with alembic migrations
# see: https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/#using-custom-metadata-and-naming-conventions
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=naming_convention)

# extension instances (global) not bound to application
db = SQLAlchemy(metadata=metadata)  # database instance
migrate = Migrate()  # migration engine instance
login = LoginManager()  # login manager instance
login.login_view = "auth.login"  # login view function (endpoint) name


def create_app(config_class=BaseConfig):
    """
    Application factory function.
    Creates and returns a Flask application instance at runtime,
    rather than a global variable.

    :param config_class: configuration class to use for application
    :return: Flask application instance
    """
    app = Flask(__name__)  # create application instance
    app.config.from_object(config_class)

    # bind extensions to application
    db.init_app(app)
    # see: https://blog.miguelgrinberg.com/post/fixing-alter-table-errors-with-flask-migrate-and-sqlite
    migrate.init_app(app, db, render_as_batch=True)
    login.init_app(app)

    # register blueprints
    register_blueprints(app)

    return app


def register_blueprints(app):
    """
    Register blueprints with the application instance.

    :param app: Flask application instance
    :return: None
    """
    from app.auth import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    from app.upload import bp as upload_bp

    app.register_blueprint(upload_bp, url_prefix="/upload")

    from app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)


from app import models
