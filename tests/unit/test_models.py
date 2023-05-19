from app.models import User, SMAnnotation


def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the username, email, and password fields are defined correctly
    """
    user = User(username="test", email="test@example.com")
    user.set_password("testpassword")
    assert user.username == "test"
    assert user.email == "test@example.com"
    assert user.password_hash != "testpassword"
    assert user.check_password("testpassword")


def test_new_sm_annotation():
    """
    GIVEN a SMAnnotation model
    WHEN a new SMAnnotation is created
    THEN check the body, timestamp, author, and user_id fields are defined correctly
    """
    user = User(username="test", email="test@example.com")
    user.set_password("testpassword")
    annotation = SMAnnotation(body="test annotation", author=user)
    assert annotation.body == "test annotation"
    assert annotation.author is user
    assert annotation.timestamp is None  # timestamp is set by database
    assert annotation.id_user is None  # id_user is set by database
