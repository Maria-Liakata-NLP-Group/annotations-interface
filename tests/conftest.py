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
