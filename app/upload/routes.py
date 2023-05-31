import os
import pickle
from datetime import datetime, timedelta
from app import db
from app.upload import bp
from app.models import SMPost, SMReply, Dataset
from werkzeug.utils import secure_filename
from flask import request, redirect, url_for, flash, render_template, current_app
from flask_login import login_required, current_user
from app.upload.forms import UploadForm


def read_pickle(file_path):
    """Read a pickle file"""
    with open(file_path, "rb") as handle:
        return pickle.load(handle)


def allowed_file(filename):
    """Check if the file extension is allowed"""
    allowed_extensions = {"pickle", "pkl"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def format_datetime(datetime_obj: datetime):
    """Format datetime object to remove microseconds"""
    datetime_obj = datetime_obj - timedelta(microseconds=datetime_obj.microsecond)
    return datetime_obj


def sm_dict_to_sql(sm_data: dict, dataset: Dataset):
    """
    Convert the social media dictionary to SQL and add it to the database.

    Args:
        sm_data (dict): The social media dictionary, read from the pickle file
            uploaded by the user.
        dataset (Dataset): The dataset object, created when the user uploaded
            the pickle file.
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
    """This is the upload route for social media datasets"""
    form = UploadForm()  # Create an instance of the UploadForm
    # This condition below is true when the request method is POST and the
    # form data passes all the defined validation checks.
    if form.validate_on_submit():
        # Check if a file is present in the request
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
            app_config = current_app.config  # Get the app config
            file_path = os.path.join(
                app_config["UPLOAD_FOLDER"], filename
            )  # Get the file path
            file.save(file_path)  # Save the file to disk
            # Create a new dataset object
            dataset = Dataset(
                name=form.name.data,
                description=form.description.data,
                author=current_user,
            )
            db.session.add(dataset)  # Add the dataset to the database
            db.session.commit()  # Commit the changes
            sm_data = read_pickle(file_path)  # Read the pickle file
            sm_dict_to_sql(
                sm_data, dataset
            )  # Convert the dictionary to SQL and add it to the database
            flash("File uploaded successfully")
            return redirect(url_for("upload.upload"))  # Redirect to the upload page
    return render_template("upload/upload.html", title="Upload dataset", form=form)
