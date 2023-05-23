def test_new_user(new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the username, email, and password fields are defined correctly
    """
    assert new_user.username == "test"
    assert new_user.email == "test@example.com"
    assert new_user.password_hash != "testpassword"
    assert new_user.check_password("testpassword")


def test_new_sm_annotation(new_sm_annotation, new_user):
    """
    GIVEN a SMAnnotation model
    WHEN a new SMAnnotation is created
    THEN check the body, timestamp, author, and user_id fields are defined correctly
    """
    assert new_sm_annotation.body == "test annotation"
    assert new_sm_annotation.author is new_user
    assert new_sm_annotation.timestamp is None  # timestamp is set by database
    assert new_sm_annotation.id_user is None  # id_user is set by database


def test_new_sm_post(new_sm_post, new_sm_annotation):
    """
    GIVEN a SMPost model
    WHEN a new SMPost is created
    THEN check the question, annotation, and id_sm_annotation fields are defined correctly
    """
    assert new_sm_post.question == "test post"
    assert new_sm_post.annotation is new_sm_annotation
    assert new_sm_post.id_sm_annotation is None  # id_sm_annotation is set by database


def test_new_sm_reply(new_sm_reply, new_sm_post):
    """
    GIVEN a SMReply model
    WHEN a new SMReply is created
    THEN check the comment, post, and id_sm_post fields are defined correctly
    """
    assert new_sm_reply.comment == "test reply"
    assert new_sm_reply.post is new_sm_post
    assert new_sm_reply.id_sm_post is None  # id_sm_post is set by database
