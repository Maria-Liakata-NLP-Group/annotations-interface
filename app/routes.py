from flask import render_template
from app import app
from flask_login import login_required


@app.route("/")
@app.route("/index")
@login_required  # This decorator ensures that the user is logged in before accessing the page
def index():
    """This is the index page"""
    return render_template("index.html", title="Home page")
