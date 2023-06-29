from app.main import bp
from flask import render_template
from flask_login import login_required, current_user


@bp.route("/")
@bp.route("/index")
@login_required  # This decorator ensures that the user is logged in before accessing the page
def index():
    """This is the index page"""
    # find all the datasets that the logged in user has access to
    datasets = current_user.datasets.all()
    return render_template("index.html", title="Home page", datasets=datasets)
