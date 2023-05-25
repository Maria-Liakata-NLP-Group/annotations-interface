import os
import pickle
from datetime import datetime, timedelta
from app import db
from app.models import SMPost, SMReply
from werkzeug.utils import secure_filename


basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../..")

upload_folder = os.path.join(
    basedir,
    "data",
    "social_media",
)

allowed_extensions = ["pkl"]

with open(file_path, "rb") as handle:
    sm_data = pickle.load(handle)

app = create_app()


def allowed_file(filename):
    """Check if the file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@bp.route("/upload", methods=["GET", "POST"])
def format_datetime(datetime_obj: datetime):
    """Format datetime object to remove microseconds"""
    datetime_obj = datetime_obj - timedelta(microseconds=datetime_obj.microsecond)
    return datetime_obj


with app.app_context():
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
