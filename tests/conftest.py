import pytest

from app import create_app, db
from app.models import User, SMAnnotation, SMPost, SMReply, Dataset
from config import TestConfig


@pytest.fixture(scope="module")
def new_user():
    """Fixture to create a new user"""
    user = User(username="test", email="test@example.com")
    user.set_password("testpassword")
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
def new_sm_annotation(new_user, new_sm_post):
    """Fixture to create a new social media annotation"""
    annotation = SMAnnotation(body="test annotation", author=new_user, post=new_sm_post)
    return annotation


@pytest.fixture(scope="module")
def new_sm_reply(new_sm_post):
    """Fixture to create a new social media reply"""
    reply = SMReply(comment="test reply", post=new_sm_post)
    return reply


@pytest.fixture(scope="module")
def new_dataset(new_user):
    """Fixture to create a new dataset"""
    dataset = Dataset(
        name="test dataset", description="test description", author=new_user
    )
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


@pytest.fixture(scope="module")
def init_database(test_client):
    """Fixture to initialize the database"""
    # Create the database and the database tables
    db.create_all()

    # Insert user data
    user1 = User(username="test1", email="test1@example.com")
    user1.set_password("testpassword1")
    user2 = User(username="test2", email="test2@example.com")
    user2.set_password("testpassword2")
    db.session.add(user1)
    db.session.add(user2)

    # Commit the changes for the users
    db.session.commit()

    yield  # this is where the testing happens!

    # Drop all the tables from the database
    db.drop_all()
