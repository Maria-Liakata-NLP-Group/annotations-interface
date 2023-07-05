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
    user.set_password("test2password")
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
def new_dataset(user_admin1, user_annotator1):
    """Fixture to create a new dataset, with two annotators"""
    dataset = Dataset(
        name="test dataset",
        description="test description",
        author=user_admin1,
    )
    dataset.annotators.append(user_admin1)
    dataset.annotators.append(user_annotator1)
    return dataset


@pytest.fixture(scope="session")
def flask_app():
    """Fixture to create a Flask app configured for testing"""
    flask_app = create_app(TestConfig)
    # Establish an application context before running the tests
    with flask_app.app_context():
        db.create_all()
        yield flask_app  # this is where the testing happens!
        db.drop_all()


@pytest.fixture(scope="module")
def test_client(flask_app):
    """Fixture to create a test client for making HTTP requests"""
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as client:
        yield client  # this is where the testing happens!


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
    dataset.annotators.append(User.query.filter_by(username="admin1").first())
    dataset.annotators.append(User.query.filter_by(username="annotator1").first())
    db.session.add(dataset)

    # Create another dataset authored by annotator1, with only one annotator
    dataset = Dataset(
        name="Psychotherapy Dataset Test",
        description="test description for psychotherapy dataset",
        author=User.query.filter_by(username="annotator1").first(),
        type=DatasetType.psychotherapy,
    )
    dataset.annotators.append(User.query.filter_by(username="annotator1").first())
    db.session.add(dataset)

    # Commit the changes to the database
    db.session.commit()

    yield  # this is where the testing happens!

    # Drop all the tables from the database
    db.drop_all()


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
