from flask import Flask
from config import BaseConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# extension instances (global) not bound to application
db = SQLAlchemy()  # database instance
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
    migrate.init_app(app, db)
    login.init_app(app)

    # register blueprints
    from app.auth import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    return app


from app import models
