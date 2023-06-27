import pytest
from datetime import date

from app import create_app, db
from app.models import User, SMAnnotation, SMPost, SMReply, Dataset, Role, Psychotherapy
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


@pytest.fixture(scope="module")
def init_database(test_client):
    """Fixture to initialize the database"""
    # Create the database and the database tables
    db.create_all()

    # Insert role data
    Role.insert_roles()

    # Insert user data
    admin1 = User(username="admin1", email="admin1@example.com")
    admin1.set_password("adminpassword1")
    annotator1 = User(username="annotator1", email="annotator1@example.com")
    annotator1.set_password("annotatorpassword1")
    db.session.add(admin1)
    db.session.add(annotator1)

    # Commit the changes for the users
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
