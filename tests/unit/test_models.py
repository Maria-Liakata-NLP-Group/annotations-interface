from app.models import User


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
