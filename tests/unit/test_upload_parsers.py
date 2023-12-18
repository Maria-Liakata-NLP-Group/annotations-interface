"""
Unit tests for the parsers module in the upload blueprint.
"""
from app.upload.parsers import read_pickle, sm_dict_to_sql, psychotherapy_df_to_sql
from app.models import Dataset, SMPost, SMReply, PSDialogTurn, PSDialogEvent
from datetime import datetime
import pytest


@pytest.mark.order(2)
def test_sm_dict_to_sql(app, db_session, insert_datasets):
    """
    Test the sm_dict_to_sql function,
    which converts the social media dictionary to SQL and adds it to the database.
    """
    sm_data = read_pickle(app.config["SM_DATASET_PATH"])
    dataset = Dataset.query.filter_by(name="Social Media Dataset Test").first()
    sm_dict_to_sql(sm_data, dataset)
    db_session.commit()

    # check that the parsing is performed correctly and the data is added to the database
    posts = SMPost.query.filter_by(id_dataset=dataset.id).all()
    assert len(posts) == 43
    replies = SMReply.query.filter_by(id_dataset=dataset.id).all()
    assert len(replies) == 92

    # more granular checks
    posts = SMPost.query.filter_by(
        user_id="746731", timeline_id="746731_1", id_dataset=dataset.id
    ).all()
    assert len(posts) == 10

    post = SMPost.query.filter_by(
        user_id="746731", timeline_id="746731_1", post_id=9602529, id_dataset=dataset.id
    ).first()
    assert (post.mood).lower() == "happy"
    replies = SMReply.query.filter_by(id_sm_post=post.id).all()
    assert len(replies) == 2


@pytest.mark.dependency()
def test_psychotherapy_df_to_sql(app, db_session):
    """
    Test the psychotherapy_df_to_sql function,
    which converts the psychotherapy dataframe to SQL and adds it to the database.
    """
    df = read_pickle(app.config["PS_DATASET_PATH"])
    dataset = Dataset.query.filter_by(name="Psychotherapy Dataset Test").first()
    psychotherapy_df_to_sql(df, dataset)
    db_session.commit()

    # check that the parsing is performed correctly and the data is added to the database
    dialog_turns = PSDialogTurn.query.filter_by(id_dataset=dataset.id).all()
    dialog_events = PSDialogEvent.query.filter_by(id_dataset=dataset.id).all()
    # check that the number of dialog turns and dialog events is correct
    # a Timestamp event marks the start of a dialog turn
    assert len(dialog_turns) == sum(df["event_speaker"] == "Timestamp")
    assert len(dialog_events) == len(df) - sum(df["event_speaker"] == "Timestamp")

    # fetch the dialog turn with dialog_turn_n = 3, i.e. fourth dialog turn
    dialog_turn = PSDialogTurn.query.filter_by(
        id_dataset=dataset.id, dialog_turn_n=3
    ).all()
    expected_timestamp = datetime.strptime(
        (df.loc[13, "event_plaintext"]).replace(" ", ""), ("%H:%M:%S")
    ).time()
    assert len(dialog_turn) == 1  # check that only one dialog turn is returned
    dialog_turn = dialog_turn[0]
    assert dialog_turn.timestamp == expected_timestamp
    assert dialog_turn.main_speaker == "Client"
    # check that the dialog turn has the correct number of dialog events
    dialog_events = PSDialogEvent.query.filter_by(
        id_dataset=dataset.id, id_ps_dialog_turn=dialog_turn.id
    ).all()
    assert len(dialog_events) == 7
    dialog_event = dialog_events[0]
    assert dialog_event.event_speaker == "Client"
    assert dialog_event.event_plaintext == df.loc[14, "event_plaintext"]
    assert (
        dialog_event.event_n == int(df.loc[14, "event_n"]) - 4
    )  # -4 because the first 4 events are Timestamps
