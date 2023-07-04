from datetime import datetime, timedelta
from app.models import SMPost, SMReply, Dataset, PSDialogTurn, PSDialogEvent
from app import db
from flask import abort
import pandas as pd
import pickle


def read_pickle(file_path: str):
    """Read a pickle file"""
    with open(file_path, "rb") as handle:
        return pickle.load(handle)


def remove_microsecs(datetime_obj: datetime):
    """Format datetime object to remove microseconds"""
    datetime_obj = datetime_obj - timedelta(microseconds=datetime_obj.microsecond)
    return datetime_obj


def format_date(date):
    """
    If the date is a string, convert it to a date object.
    If the date is a datetime object, convert it to a date object.
    If the date is a date object, return it as is.
    """
    if isinstance(date, str):
        try:
            date_obj = datetime.strptime(date, "%m/%d/%Y").date()
        except ValueError:
            date_obj = datetime.strptime(date, "%m-%d-%Y").date()
        return date_obj
    elif isinstance(date, datetime):
        return date.date()
    elif isinstance(date, date):
        return date


def sm_dict_to_sql(sm_data: dict, dataset: Dataset):
    """
    Convert the social media dictionary to SQL and add it to the database.

    Args:
        sm_data (dict): The social media dictionary, read from the pickle file uploaded by the user.
        dataset (Dataset): The dataset object, created when the user uploaded the pickle file.
    """
    try:
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
                        date=remove_microsecs(post["date"]),
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
                            date=remove_microsecs(reply["date"]),
                            ldate=datetime(*reply["ldate"]),
                            comment=reply["comment"],
                            post=sm_post,
                            dataset=dataset,
                        )
                        db.session.add(sm_reply)
    except:
        abort(400)  # raise a HTTP 400 Bad Request error


def psychotherapy_df_to_sql(df: pd.DataFrame, dataset: Dataset):
    """
    Convert the psychotherapy dataframe to SQL and add it to the database.

    Args:
        df (pd.DataFrame): The psychotherapy dataframe, read from the pickle file uploaded by the user.
        dataset (Dataset): The dataset object, created when the user uploaded the pickle file.
    """
    try:
        # find the row indices where the "dialog_turn_main_speaker" column is "timestamp"
        # these are the rows that mark the start of a dialog turn
        dialog_indices = df.loc[df["dialog_turn_main_speaker"] == "Timestamp"].index
        dialog_counter = 0  # counter for the dialog turns
        event_counter = 0  # counter for the dialog events
        for i, (index, row) in enumerate(df.loc[dialog_indices].iterrows()):
            # Each row in the dataframe is a different speech turn
            # A dialog turn can contain multiple speech turns
            if i < len(dialog_indices) - 1:
                next_index = dialog_indices[i + 1]
            else:
                next_index = len(df)
            # create a PSDialogTurn object for each dialog turn
            ps_dialog_turn = PSDialogTurn(
                c_code=row["c_code"],
                # if "t_init" is not in the dataframe, set it to None
                t_init=row["t_init"] if "t_init" in df.columns else None,
                date=format_date(row["date"]),
                # timestamp given as a string in "event_plaintext" column
                timestamp=datetime.strptime(
                    (row["event_plaintext"]).replace(" ", ""), "%H:%M:%S"
                ).time(),
                # then "main_speaker" for this dialog turn is contained in
                # the next row of the "dialog_turn_main_speaker" column
                main_speaker=df.loc[index + 1, "dialog_turn_main_speaker"],
                session_n=int(row["session_n"]),
                dialog_turn_n=dialog_counter,
                dataset=dataset,
            )
            dialog_counter += 1
            db.session.add(ps_dialog_turn)  # add the dialog turn to the database
            # create a PSDialogEvent object for each speech turn in the dialog turn
            for j in range(index + 1, next_index):
                ps_dialog_event = PSDialogEvent(
                    event_n=event_counter,
                    event_speaker=df.loc[j, "event_speaker"],
                    event_plain_text=df.loc[j, "event_plaintext"],
                    dialog_turn=ps_dialog_turn,
                    dataset=dataset,
                )
                event_counter += 1
                db.session.add(ps_dialog_event)  # add the dialog event to the database
    except:
        abort(400)  # raise a HTTP 400 Bad Request error
