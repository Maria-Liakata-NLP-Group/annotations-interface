import pytest
from datetime import datetime, date

from app import create_app, db
from app.models import (
    User,
    SMAnnotation,
    SMPost,
    SMReply,
    Dataset,
    Role,
    PSDialogTurn,
    PSDialogEvent,
    DatasetType,
    PSDialogTurnAnnotationClient,
    PSDialogTurnAnnotationTherapist,
    PSDialogTurnAnnotationDyad,
)
from app.utils import (
    SubLabelsAClient,
    SubLabelsATherapist,
    SubLabelsBClient,
    SubLabelsBTherapist,
    SubLabelsADyad,
    SubLabelsBDyad,
    LabelStrengthAClient,
    LabelStrengthBTherapist,
    LabelStrengthADyad,
)
from config import TestConfig
from app.upload.parsers import read_pickle, psychotherapy_df_to_sql


@pytest.fixture(scope="module")
def user_admin1():
    """Fixture to create a new admin user"""
    user = User(username="admin1", email="admin1@example.com")
    user.set_password("admin1password")
    return user


@pytest.fixture(scope="module")
def user_annotator1():
    """Fixture to create a new annotator user"""
    user = User(username="annotator1", email="annotator1@example.com")
    user.set_password("annotator1password")
    return user


@pytest.fixture(scope="module")
def new_sm_post(new_sm_dataset):
    """Fixture to create a new social media post"""
    post = SMPost(
        question="test post",
        user_id="1",
        timeline_id="1",
        post_id=1,
        dataset=new_sm_dataset,
    )
    return post


@pytest.fixture(scope="module")
def new_sm_annotation(user_admin1, new_sm_post):
    """Fixture to create a new social media annotation"""
    annotation = SMAnnotation(
        body="test annotation", author=user_admin1, post=new_sm_post
    )
    return annotation


@pytest.fixture(scope="module")
def new_sm_reply(new_sm_post, new_sm_dataset):
    """Fixture to create a new social media reply"""
    reply = SMReply(
        comment="test reply",
        post=new_sm_post,
        dataset=new_sm_dataset,
    )
    return reply


@pytest.fixture(scope="module")
def new_sm_dataset(user_admin1, user_annotator1):
    """Fixture to create a new social media dataset authored by admin1, with two annotators"""
    dataset = Dataset(
        name="Social Media Dataset Test",
        description="test description for SM dataset",
        author=user_admin1,
        type=DatasetType.sm_thread,
    )
    dataset.annotators.append(user_admin1)
    dataset.annotators.append(user_annotator1)
    return dataset


@pytest.fixture(scope="module")
def new_ps_dataset(user_annotator1):
    """Fixture to create a new psychotherapy dataset authored by annotator1, with only one annotator"""
    dataset = Dataset(
        name="Psychotherapy Dataset Test",
        description="test description for psychotherapy dataset",
        author=user_annotator1,
        type=DatasetType.psychotherapy,
    )
    dataset.annotators.append(user_annotator1)
    return dataset


@pytest.fixture(scope="module")
def flask_app():
    """Fixture to create a Flask app configured for testing"""
    flask_app = create_app(TestConfig)
    # Establish an application context before running the tests
    with flask_app.app_context():
        db.create_all()
        Role.insert_roles()
        yield flask_app  # this is where the testing happens!
        db.drop_all()


@pytest.fixture(scope="module")
def db_session(flask_app):
    """Fixture to create a database session for testing"""
    # Establish an application context before running the tests
    with flask_app.app_context():
        yield db.session


@pytest.fixture(scope="function")
def test_client(flask_app):
    """Fixture to create a test client for making HTTP requests"""
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as client:
        yield client  # this is where the testing happens!


@pytest.fixture(scope="function")
def insert_users(db_session, user_admin1, user_annotator1):
    """Fixture to insert users into the database"""
    db_session.add(user_admin1)
    db_session.add(user_annotator1)
    db_session.commit()


@pytest.fixture(scope="module")
def insert_datasets(db_session, new_sm_dataset, new_ps_dataset):
    """Fixture to insert datasets into the database"""
    db_session.add(new_sm_dataset)
    db_session.add(new_ps_dataset)
    db_session.commit()


@pytest.fixture(scope="module")
def insert_ps_dialog_turns(flask_app, db_session, insert_datasets):
    """Fixture to insert psychotherapy dialog turns (and corresponding events) into the database"""
    df = read_pickle(flask_app.config["PS_DATASET_PATH"])
    dataset = Dataset.query.filter_by(name="Psychotherapy Dataset Test").first()
    psychotherapy_df_to_sql(df, dataset)
    db_session.commit()


@pytest.fixture(scope="module")
def new_ps_dialog_turn(new_ps_dataset):
    """Fixture to create a new psychotherapy dialog turn"""
    dialog_turn = PSDialogTurn(
        c_code="ab1234",
        date=date.today(),
        timestamp=datetime.strptime("00:00:00", "%H:%M:%S").time(),
        main_speaker="Client",
        session_n=1,
        dialog_turn_n=1,
        dataset=new_ps_dataset,
    )
    return dialog_turn


@pytest.fixture(scope="module")
def new_ps_dialog_event(new_ps_dataset, new_ps_dialog_turn):
    """Fixture to create a new psychotherapy dialog event or speech turn"""
    dialog_event = PSDialogEvent(
        event_n=1,
        event_speaker="Therapist",
        event_plaintext="Hello, how are you?",
        dialog_turn=new_ps_dialog_turn,
        dataset=new_ps_dataset,
    )
    return dialog_event


@pytest.fixture(scope="module")
def new_ps_dialog_turn_annotation_client(
    new_ps_dataset, new_ps_dialog_turn, user_annotator1
):
    """Fixture to create a new psychotherapy dialog turn annotation for the client"""
    dialog_turn_annotation = PSDialogTurnAnnotationClient(
        label_a=SubLabelsAClient.attachment,
        label_b=SubLabelsBClient.attachment,
        strength_a=LabelStrengthAClient.moderately_adaptive,
        comment_a="test comment a",
        comment_b="test comment b",
        comment_summary="test comment summary",
        author=user_annotator1,
        dataset=new_ps_dataset,
    )
    dialog_turn_annotation.dialog_turns.append(new_ps_dialog_turn)
    return dialog_turn_annotation


@pytest.fixture(scope="module")
def new_ps_dialog_turn_annotation_therapist(
    new_ps_dataset, new_ps_dialog_turn, user_annotator1
):
    """Fixture to create a new psychotherapy dialog turn annotation for the therapist"""
    dialog_turn_annotation = PSDialogTurnAnnotationTherapist(
        label_a=SubLabelsATherapist.emotional,
        label_b=SubLabelsBTherapist.reframing,
        strength_b=LabelStrengthBTherapist.high,
        comment_a="test comment a",
        comment_b="test comment b",
        comment_summary="test comment summary",
        author=user_annotator1,
        dialog_turn=new_ps_dialog_turn,
        dataset=new_ps_dataset,
    )
    return dialog_turn_annotation


@pytest.fixture(scope="module")
def new_ps_dialog_turn_annotation_dyad(
    new_ps_dataset, new_ps_dialog_turn, user_annotator1
):
    """Fixture to create a new psychotherapy dialog turn annotation for the dyad"""
    dialog_turn_annotation = PSDialogTurnAnnotationDyad(
        label_a=SubLabelsADyad.bond,
        label_b=SubLabelsBDyad.other,
        strength_a=LabelStrengthADyad.medium,
        comment_a="test comment a",
        comment_b="test comment b",
        comment_summary="test comment summary",
        author=user_annotator1,
        dialog_turn=new_ps_dialog_turn,
        dataset=new_ps_dataset,
    )
    return dialog_turn_annotation
