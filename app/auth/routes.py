from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm
from app.models import User


@bp.route("/login", methods=["GET", "POST"])
def login():
    """This is the login page"""
    if current_user.is_authenticated:
        # If the user is already logged in, redirect to the index page
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        # This only runs if the form is submitted (`POST`) and validated
        user = User.query.filter_by(
            username=form.username.data
        ).first()  # Get the user from the database
        # Check if the user exists and if the password is correct
        if user is None or not user.check_password(form.password.data):
            # If the user doesn't exist or the password is incorrect, redirect to the login page
            flash(
                "Invalid username or password"
            )  # flash() registers a message to show to the user
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)  # otherwise, log the user in
        next_page = request.args.get("next")  # Get the next page from the URL
        if not next_page or url_parse(next_page).netloc != "":
            # If there is no next page or the next page is not relative, redirect to the index page
            next_page = url_for("index")
        return redirect(next_page)  # otherwise, redirect to the next page
    return render_template("auth/login.html", title="Sign In", form=form)


@bp.route("/logout")
def logout():
    """This is the logout page"""
    logout_user()
    return redirect(url_for("index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    """This is the register page"""
    if current_user.is_authenticated:
        # If the user is already logged in, redirect to the index page
        return redirect(url_for("index"))
    form = RegisterForm()
    if form.validate_on_submit():
        # This only runs if the form is submitted (`POST`) and validated
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        # Add the user to the database
        db.session.add(user)
        db.session.commit()
        flash("You have successfully registered!")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", title="Register", form=form)
