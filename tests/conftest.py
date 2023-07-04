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
)
from config import TestConfig


@pytest.fixture(scope="module")
def new_user():
    """Fixture to create a new user"""
    user = User(username="test", email="test@example.com")
    user.set_password("testpassword")
    return user


@pytest.fixture(scope="module")
def another_user():
    """Fixture to create another user"""
    user = User(username="test2", email="test2@example.com")
    user.set_password("test2password")
    return user


@pytest.fixture(scope="module")
def new_sm_post(new_dataset):
    """Fixture to create a new social media post"""
    post = SMPost(
        question="test post",
        user_id="1",
        timeline_id="1",
        post_id=1,
        dataset=new_dataset,
    )
    return post


@pytest.fixture(scope="module")
def new_sm_annotation(new_user, new_sm_post):
    """Fixture to create a new social media annotation"""
    annotation = SMAnnotation(body="test annotation", author=new_user, post=new_sm_post)
    return annotation


@pytest.fixture(scope="module")
def new_sm_reply(new_sm_post, new_dataset):
    """Fixture to create a new social media reply"""
    reply = SMReply(
        comment="test reply",
        post=new_sm_post,
        dataset=new_dataset,
    )
    return reply


@pytest.fixture(scope="module")
def new_dataset(new_user, another_user):
    """Fixture to create a new dataset, with two annotators"""
    dataset = Dataset(
        name="test dataset",
        description="test description",
        author=new_user,
    )
    dataset.annotators.append(new_user)
    dataset.annotators.append(another_user)
    return dataset


@pytest.fixture(scope="module")
def test_client():
    """Fixture to create a test client"""
    # Create the Flask app configured for testing
    flask_app = create_app(TestConfig)
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context before running the tests
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!


def create_users_for_db():
    """Helper function to create users for the database"""
    admin1 = User(username="admin1", email="admin1@example.com")
    admin1.set_password("adminpassword1")
    annotator1 = User(username="annotator1", email="annotator1@example.com")
    annotator1.set_password("annotatorpassword1")
    db.session.add(admin1)
    db.session.add(annotator1)


@pytest.fixture(scope="module")
def init_database(test_client):
    """Fixture to initialize the database"""
    # Create the database and the database tables
    db.create_all()

    # Insert role data
    Role.insert_roles()

    # Insert user data
    create_users_for_db()

    # Commit the changes for the users
    db.session.commit()

    yield  # this is where the testing happens!

    # Drop all the tables from the database
    db.drop_all()


@pytest.fixture(scope="module")
def init_database_with_datasets(test_client):
    """Fixture to initialize the database with datasets"""
    # Create the database and the database tables
    db.create_all()

    # Insert role data
    Role.insert_roles()

    # Insert user data
    create_users_for_db()

    # Create a dataset authored by admin1, with two annotators
    dataset = Dataset(
        name="Social Media Dataset Test",
        description="test description for SM dataset",
        author=User.query.filter_by(username="admin1").first(),
        type=DatasetType.sm_thread,
    )
    db.session.add(dataset)
    dataset.annotators.append(User.query.filter_by(username="admin1").first())
    dataset.annotators.append(User.query.filter_by(username="annotator1").first())

    # Create another dataset authored by annotator1, with only one annotator
    dataset = Dataset(
        name="Psychotherapy Dataset Test",
        description="test description for psychotherapy dataset",
        author=User.query.filter_by(username="annotator1").first(),
        type=DatasetType.psychotherapy,
    )
    db.session.add(dataset)
    dataset.annotators.append(User.query.filter_by(username="annotator1").first())

    # Commit the changes to the database
    db.session.commit()

    yield  # this is where the testing happens!

    # Drop all the tables from the database
    db.drop_all()


@pytest.fixture(scope="module")
def new_ps_dialog_turn(new_dataset):
    """Fixture to create a new psychotherapy dialog turn"""
    dialog_turn = PSDialogTurn(
        c_code="ab1234",
        date=date.today(),
        timestamp=datetime.strptime("00:00:00", "%H:%M:%S").time(),
        main_speaker="Client",
        session_n=1,
        dialog_turn_n=1,
        dataset=new_dataset,
    )
    return dialog_turn


@pytest.fixture(scope="module")
def new_ps_dialog_event(new_dataset, new_ps_dialog_turn):
    """Fixture to create a new psychotherapy dialog event or speech turn"""
    dialog_event = PSDialogEvent(
        event_n=1,
        event_speaker="Therapist",
        event_plaintext="Hello, how are you?",
        dialog_turn=new_ps_dialog_turn,
        dataset=new_dataset,
    )
    return dialog_event
