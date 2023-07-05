import pytest
from datetime import date

from app import create_app, db
from app.models import (
    User,
    SMAnnotation,
    SMPost,
    SMReply,
    Dataset,
    Role,
    Psychotherapy,
    DatasetType,
)
from config import TestConfig


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
def new_sm_post():
    """Fixture to create a new social media post"""
    post = SMPost(
        question="test post",
        user_id="1",
        timeline_id="1",
        post_id=1,
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
def new_sm_reply(new_sm_post):
    """Fixture to create a new social media reply"""
    reply = SMReply(comment="test reply", post=new_sm_post)
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
def new_psychotherapy_event():
    """Fixture to create a new psychotherapy session turn of speech"""
    psychotherapy = Psychotherapy(
        event_id=0,
        event_text="test event",
        event_speaker="test speaker",
        date=date.today(),
        t_init="ab",
        c_code="bc1234",
    )
    return psychotherapy
