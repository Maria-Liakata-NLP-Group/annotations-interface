import os
import pickle
from datetime import datetime, timedelta
from app import db, app
from app.upload import bp
from app.models import SMPost, SMReply
from werkzeug.utils import secure_filename
from flask import request, redirect, url_for, flash
from flask_login import login_required


def read_pickle(file_path):
    """Read a pickle file"""
    with open(file_path, "rb") as handle:
        return pickle.load(handle)


def allowed_file(filename):
    """Check if the file extension is allowed"""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def format_datetime(datetime_obj: datetime):
    """Format datetime object to remove microseconds"""
    datetime_obj = datetime_obj - timedelta(microseconds=datetime_obj.microsecond)
    return datetime_obj


def dict_to_sql(sm_data: dict):
    """
    Convert the dictionary to SQL and add it to the database
    """
    users = list(sm_data.keys())
    for user in users:
        timelines = list(sm_data[user].keys())
        for timeline in timelines:
            posts = sm_data[user][timeline]
            for post in posts:
                sm_post = SMPost(
                    user_id=user,
                    timeline_id=timeline,
                    post_id=post["post_id"],
                    mood=post["mood"],
                    date=format_datetime(post["date"]),
                    ldate=datetime(*post["ldate"]),
                    question=post["question"],
                )
                db.session.add(sm_post)
                replies = post["replies"]
                for reply in replies:
                    sm_reply = SMReply(
                        reply_id=reply["id"],
                        user_id=reply["user"],
                        date=format_datetime(reply["date"]),
                        ldate=datetime(*reply["ldate"]),
                        comment=reply["comment"],
                        post=sm_post,
                    )
                    db.session.add(sm_reply)
            db.session.commit()  # commit after each timeline


@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """This is the file upload page"""
    if request.method == "POST":
        # Check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)  # Redirect to the upload page
        file = request.files["file"]  # Get the file from the request
        # If the user does not select a file,
        # the browser submits an empty file without a filename
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)  # Redirect to the upload page
        if file and allowed_file(file.filename):  # If the file is valid
            # Secure the filename before saving it
            filename = secure_filename(file.filename)  # Get the filename
            file_path = os.path.join(
                app.config["UPLOAD_FOLDER"], filename
            )  # Get the file path
            file.save(file_path)  # Save the file
            flash("File uploaded successfully")
            sm_data = read_pickle(file_path)  # Read the pickle file
            dict_to_sql(
                sm_data
            )  # Convert the dictionary to SQL and add it to the database
            return redirect(url_for("main.index"))  # Redirect to the index page
