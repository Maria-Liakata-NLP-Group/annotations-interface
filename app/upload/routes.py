import os
import pickle
from datetime import datetime, timedelta
from app import db
from app.upload import bp
from app.models import SMPost, SMReply, Dataset
from werkzeug.utils import secure_filename
from flask import request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from app.upload.forms import UploadForm

allowed_extensions = {"pickle", "pkl"}
upload_folder = os.path.join(os.path.dirname(__file__), "../..", "data")


def read_pickle(file_path):
    """Read a pickle file"""
    with open(file_path, "rb") as handle:
        return pickle.load(handle)


def allowed_file(filename):
    """Check if the file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def format_datetime(datetime_obj: datetime):
    """Format datetime object to remove microseconds"""
    datetime_obj = datetime_obj - timedelta(microseconds=datetime_obj.microsecond)
    return datetime_obj


def dict_to_sql(sm_data: dict, dataset: Dataset = None):
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
                    dataset=dataset,
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
    form = UploadForm()  # Create an instance of the UploadForm
    if form.validate_on_submit():
        # Check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(url_for("upload.upload"))  # Redirect to the upload page
        file = request.files["file"]  # Get the file from the request
        # If the user does not select a file,
        # the browser submits an empty file without a filename
        if file.filename == "":
            flash("No selected file")
            return redirect(url_for("upload.upload"))  # Redirect to the upload page
        if file and allowed_file(file.filename):  # If the file is valid
            # Secure the filename before saving it
            filename = secure_filename(file.filename)  # Get the filename
            file_path = os.path.join(upload_folder, filename)  # Get the file path
            file.save(file_path)  # Save the file to disk
            dataset = Dataset(
                name=form.name.data,
                description=form.description.data,
                author=current_user,
            )
            db.session.add(dataset)  # Add the dataset to the database
            db.session.commit()  # Commit the changes
            sm_data = read_pickle(file_path)  # Read the pickle file
            dict_to_sql(
                sm_data, dataset
            )  # Convert the dictionary to SQL and add it to the database
            flash("File uploaded successfully")
            return redirect(url_for("main.index"))  # Redirect to the index page
    return render_template("upload/upload.html", title="Upload new dataset", form=form)
