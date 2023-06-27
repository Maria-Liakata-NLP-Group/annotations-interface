import os
import pickle
from datetime import datetime, timedelta, date
import pandas as pd
from app import db
from app.upload import bp
from app.models import SMPost, SMReply, Dataset, User, Psychotherapy, DatasetType
from werkzeug.utils import secure_filename
from flask import request, redirect, url_for, flash, render_template, current_app
from flask_login import login_required, current_user
from app.upload.forms import UploadForm


def read_pickle(file_path: str):
    """Read a pickle file"""
    with open(file_path, "rb") as handle:
        return pickle.load(handle)


def allowed_file(filename: str):
    """Check if the file extension is allowed"""
    allowed_extensions = {"pickle", "pkl"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def format_datetime(datetime_obj: datetime):
    """Format datetime object to remove microseconds"""
    datetime_obj = datetime_obj - timedelta(microseconds=datetime_obj.microsecond)
    return datetime_obj


def format_date(date_str: str):
    """Parse the date string and return a date object"""
    try:
        date_obj = datetime.strptime(date_str, "%m/%d/%Y").date()
    except ValueError:
        date_obj = datetime.strptime(date_str, "%m-%d-%Y").date()
    return date_obj


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
                        dataset=dataset,
                    )
                    db.session.add(sm_reply)


def psychotherapy_df_to_sql(psychotherapy_df: pd.DataFrame, dataset: Dataset):
    """
    Convert the psychotherapy dataframe to SQL and add it to the database.

    Args:
        psychotherapy_df (pd.DataFrame): The psychotherapy dataframe, read from
            the pickle file uploaded by the user.
        dataset (Dataset): The dataset object, created when the user uploaded
            the pickle file.
    """
    for index, row in psychotherapy_df.iterrows():
        # each row is a turn of speech (event_text) by the therapist,
        # patient or annotator (event_speaker)
        psychotherapy = Psychotherapy(
            event_id=index,
            event_text=row.event_plaintext,
            event_speaker=row.event_speaker,
            date=format_date(row.date),
            t_init=row.t_init,
            c_code=row.c_code,
            dataset=dataset,
        )
        db.session.add(psychotherapy)


def form_choices():
    """Depending on the user role, return a list of annotators to choose from"""
    if current_user.is_administrator():
        # the administrator can choose who annotates the dataset
        users = User.query.order_by(User.username.asc()).all()
        # create a list of tuples with the user id and username
        # the user id is the value of the option, and the username is the text
        choices = [(user.id, user.username) for user in users]
    else:
        # regular users can only annotate their own datasets
        choices = [(current_user.id, current_user.username)]
    return choices


def get_file_path(filename: str):
    """
    Get the path of the file that will be saved to disk.
    The path is the UPLOAD_FOLDER from the app config, joined with the filename.
    """
    app_config = current_app.config  # Get the app config
    file_path = os.path.join(app_config["UPLOAD_FOLDER"], filename)
    return file_path


def new_dataset_to_db(form: UploadForm, dataset_type: DatasetType):
    """Create a new dataset object and add it to the database"""
    dataset = Dataset(
        name=form.name.data,
        description=form.description.data,
        author=current_user,
        type=dataset_type,
    )
    for annotator_id in form.annotators.data:
        annotator = User.query.get(annotator_id)
        dataset.annotators.append(annotator)
    db.session.add(dataset)  # Add the dataset to the database
    return dataset


@bp.route("/upload_sm", methods=["GET", "POST"])
@login_required
def upload_sm():
    """This is the upload route for social media datasets"""
    form = UploadForm()  # Create an instance of the UploadForm
    form.annotators.choices = form_choices()  # Set the choices for the annotators
    # This condition below is true when the request method is POST and the
    # form data passes all the defined validation checks.
    if form.validate_on_submit():
        # Check if a file is present in the request
        if "file" not in request.files:
            flash("No file part")
            return redirect(
                url_for("upload.upload_sm")
            )  # Redirect to the upload_sm page
        file = request.files["file"]  # Get the file from the request
        # If the user does not select a file,
        # the browser submits an empty file without a filename
        if file.filename == "":
            flash("No selected file")
            return redirect(
                url_for("upload.upload_sm")
            )  # Redirect to the upload_sm page
        if file and allowed_file(file.filename):  # If the file is valid
            # Secure the filename before saving it
            filename = secure_filename(file.filename)  # Get the filename
            file_path = get_file_path(filename)  # Get the file path
            file.save(file_path)  # Save the file to disk
            # Create a new dataset object and add it to the database
            dataset_type = DatasetType.sm_thread
            dataset = new_dataset_to_db(form, dataset_type)
            sm_data = read_pickle(file_path)  # Read the pickle file
            sm_dict_to_sql(
                sm_data, dataset
            )  # Convert the dictionary to SQL and add it to the database
            db.session.commit()  # Commit the changes to the database
            flash("File uploaded successfully")
            return redirect(
                url_for("upload.upload_sm")
            )  # Redirect to the upload_sm page
    return render_template(
        "upload/upload.html",
        title="Upload dataset",
        heading="Upload new social media dataset",
        form=form,
    )


@bp.route("/upload_psychotherapy", methods=["GET", "POST"])
@login_required
def upload_psychotherapy():
    """This is the upload route for psychotherapy session datasets"""
    form = UploadForm()  # Create an instance of the UploadForm
    form.annotators.choices = form_choices()  # Set the choices for the annotators
    # This condition below is true when the request method is POST and the
    # form data passes all the defined validation checks.
    if form.validate_on_submit():
        # Check if a file is present in the request
        if "file" not in request.files:
            flash("No file part")
            return redirect(
                url_for("upload.upload_psychotherapy")
            )  # Redirect to the upload_psychotherapy page
        file = request.files["file"]  # Get the file from the request
        # If the user does not select a file,
        # the browser submits an empty file without a filename
        if file.filename == "":
            flash("No selected file")
            return redirect(
                url_for("upload.upload_psychotherapy")
            )  # Redirect to the upload_psychotherapy page
        if file and allowed_file(file.filename):  # If the file is valid
            # Secure the filename before saving it
            filename = secure_filename(file.filename)  # Get the filename
            file_path = get_file_path(filename)  # Get the file path
            file.save(file_path)  # Save the file to disk
            # Create a new dataset object and add it to the database
            dataset_type = DatasetType.psychotherapy
            dataset = new_dataset_to_db(form, dataset_type)
            psychotherapy_data = read_pickle(file_path)  # Read the pickle file
            psychotherapy_df_to_sql(
                psychotherapy_data, dataset
            )  # Convert the dataframe to SQL and add it to the database
            db.session.commit()  # Commit the changes to the database
            flash("File uploaded successfully")
            return redirect(
                url_for("upload.upload_psychotherapy")
            )  # Redirect to the upload_sm page
    return render_template(
        "upload/upload.html",
        title="Upload dataset",
        heading="Upload new psychotherapy session dataset",
        form=form,
    )
