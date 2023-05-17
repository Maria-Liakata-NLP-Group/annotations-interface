from app.models import User, Post


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


def test_new_post():
    """
    GIVEN a Post model
    WHEN a new Post is created
    THEN check the body, timestamp, author, and user_id fields are defined correctly
    """
    user = User(username="test", email="test@example.com")
    user.set_password("testpassword")
    post = Post(body="test post", author=user)
    assert post.body == "test post"
    assert post.author is user
    assert post.timestamp is None  # timestamp is set by database
    assert post.user_id is None  # user_id is set by database
