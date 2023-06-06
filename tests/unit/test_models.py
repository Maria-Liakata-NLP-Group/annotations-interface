def test_new_user(init_database, new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the username, email, and password fields are defined correctly
    """
    assert new_user.username == "test"
    assert new_user.email == "test@example.com"
    assert new_user.password_hash != "testpassword"
    assert new_user.check_password("testpassword")


def test_new_sm_annotation(new_sm_annotation, new_user, new_sm_post):
    """
    GIVEN a SMAnnotation model
    WHEN a new SMAnnotation is created
    THEN check the body, author, post, timestamp, id_user, and id_sm_post fields are defined correctly
    """
    assert new_sm_annotation.body == "test annotation"
    assert new_sm_annotation.author is new_user
    assert new_sm_annotation.post is new_sm_post
    assert new_sm_annotation.timestamp is None  # timestamp is set by database
    assert new_sm_annotation.id_user is None  # id_user is set by database
    assert new_sm_annotation.id_sm_post is None  # id_sm_post is set by database


def test_new_sm_post(new_sm_post):
    """
    GIVEN a SMPost model
    WHEN a new SMPost is created
    THEN check the question, user_id, timeline_id, and post_id fields are defined correctly
    """
    assert new_sm_post.question == "test post"
    assert new_sm_post.user_id == "1"
    assert new_sm_post.timeline_id == "1"
    assert new_sm_post.post_id == 1


def test_new_sm_reply(new_sm_reply, new_sm_post):
    """
    GIVEN a SMReply model
    WHEN a new SMReply is created
    THEN check the comment, post, and id_sm_post fields are defined correctly
    """
    assert new_sm_reply.comment == "test reply"
    assert new_sm_reply.post is new_sm_post
    assert new_sm_reply.id_sm_post is None  # id_sm_post is set by database


def test_new_dataset(new_dataset, new_user):
    """
    GIVEN a Dataset model
    WHEN a new Dataset is created
    THEN check the name, description, author, and id fields are defined correctly
    """
    assert new_dataset.name == "test dataset"
    assert new_dataset.description == "test description"
    assert new_dataset.author is new_user
    assert new_dataset.id is None  # id is set by database


def test_roles(init_database):
    """
    GIVEN a Role model
    WHEN a new Role is created
    THEN check the name field is defined correctly and the role has the correct permissions
    """
    # Role names are defined in app/models.py,
    # and are added to the database configured for testing in conftest.py
    from app.models import Role, Permission

    annotator = Role.query.filter_by(name="Annotator").first()
    admin = Role.query.filter_by(name="Administrator").first()

    assert annotator is not None
    assert admin is not None
    assert annotator.has_permission(Permission.READ) and annotator.has_permission(
        Permission.WRITE
    )
    assert (
        admin.has_permission(Permission.READ)
        and admin.has_permission(Permission.WRITE)
        and admin.has_permission(Permission.ADMIN)
    )
