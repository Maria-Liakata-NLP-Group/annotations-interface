from app.models import User, SMAnnotation, SMPost, SMReply


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


def test_new_sm_post():
    """
    GIVEN a SMPost model
    WHEN a new SMPost is created
    THEN check the question, annotation, and id_sm_annotation fields are defined correctly
    """
    annotation = SMAnnotation(body="test annotation")
    post = SMPost(question="test post", annotation=annotation)
    assert post.question == "test post"
    assert post.annotation is annotation
    assert post.id_sm_annotation is None  # id_sm_annotation is set by database


def test_new_sm_reply():
    """
    GIVEN a SMReply model
    WHEN a new SMReply is created
    THEN check the comment, post, and id_sm_post fields are defined correctly
    """
    post = SMPost(question="test post")
    reply = SMReply(comment="test reply", post=post)
    assert reply.comment == "test reply"
    assert reply.post is post
    assert reply.id_sm_post is None  # id_sm_post is set by database
