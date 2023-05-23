from flask import Flask
from config import BaseConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)  # database instance
migrate = Migrate(app, db)  # migration engine instance
login = LoginManager(app)  # login manager instance
login.login_view = "auth.login"  # login view function (endpoint) name

from app.auth import bp as auth_bp

app.register_blueprint(auth_bp, url_prefix="/auth")

from app.main import bp as main_bp

app.register_blueprint(main_bp)

from app import models
from app.main import routes
