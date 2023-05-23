import pytest

from app import create_app
from app.models import User, SMAnnotation, SMPost, SMReply
from config import TestConfig


@pytest.fixture(scope="module")
def new_user():
    """Fixture to create a new user"""
    user = User(username="test", email="test@example.com")
    user.set_password("testpassword")
    return user


@pytest.fixture(scope="module")
def new_sm_annotation(new_user):
    """Fixture to create a new social media annotation"""
    annotation = SMAnnotation(body="test annotation", author=new_user)
    return annotation


@pytest.fixture(scope="module")
def new_sm_post(new_sm_annotation):
    """Fixture to create a new social media post"""
    post = SMPost(question="test post", annotation=new_sm_annotation)
    return post


@pytest.fixture(scope="module")
def new_sm_reply(new_sm_post):
    """Fixture to create a new social media reply"""
    reply = SMReply(comment="test reply", post=new_sm_post)
    return reply


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
