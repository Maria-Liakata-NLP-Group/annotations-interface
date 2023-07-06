# unit tests for parsers.py of the upload blueprint
from app.upload.parsers import read_pickle, sm_dict_to_sql
from app.models import Dataset, SMPost, SMReply


def test_sm_dict_to_sql(flask_app, db_session, insert_datasets):
    """
    Test the sm_dict_to_sql function,
    which converts the social media dictionary to SQL and adds it to the database.
    """
    sm_data = read_pickle(flask_app.config["SM_DATASET_PATH"])
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
