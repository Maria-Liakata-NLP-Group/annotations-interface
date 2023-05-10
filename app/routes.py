from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user
from app.models import User


@app.route("/")
@app.route("/index")
def index():
    """This is the index page"""
    user = {"email": "random.user@random.com"}
    return render_template("index.html", user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    """This is the login page"""
    if current_user.is_authenticated:
        # If the user is already logged in, redirect to the index page
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        # This only runs if the form is submitted (`POST`) and validated
        user = User.query.filter_by(
            email=form.email.data
        ).first()  # Get the user from the database
        # Check if the user exists and if the password is correct
        if user is None or not user.check_password(form.password.data):
            # If the user doesn't exist or the password is incorrect, redirect to the login page
            flash(
                "Invalid username or password"
            )  # flash() registers a message to show to the user
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)  # otherwise, log the user in
        return redirect(url_for("index"))
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    """This is the logout page"""
    logout_user()
    return redirect(url_for("index"))
