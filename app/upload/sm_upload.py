import os
import pickle
from datetime import datetime, timedelta

# fix the import error
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from app.models import SMPost, SMReply
from app import create_app, db


basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../..")

file_path = os.path.join(
    basedir,
    "data",
    "social_media",
    "timelines_example_lorem.pickle",
)

with open(file_path, "rb") as handle:
    sm_data = pickle.load(handle)

app = create_app()


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
