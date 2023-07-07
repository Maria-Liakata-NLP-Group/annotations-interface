from flask import Blueprint

bp = Blueprint("annotate", __name__)

from app.annotate import routes
