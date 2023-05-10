from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm


@app.route("/")
@app.route("/index")
def index():
    """This is the index page"""
    user = {"email": "random.user@random.com"}
    return render_template("index.html", user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    """This is the login page"""
    form = LoginForm()
    if form.validate_on_submit():
        # This only runs if the form is submitted (`POST`) and validated
        # flash() registers a message to show to the user
        flash(
            "Login requested for user {}, remember_me={}".format(
                form.email.data, form.remember_me.data
            )
        )
        return redirect(url_for("index"))
    return render_template("login.html", title="Sign In", form=form)
