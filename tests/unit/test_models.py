from datetime import date


def test_new_user(insert_users, user_admin1):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the username, email, and password fields are defined correctly
    """
    assert user_admin1.username == "admin1"
    assert user_admin1.email == "admin1@example.com"
    assert user_admin1.password_hash != "admin1password"
    assert user_admin1.check_password("admin1password")


def test_new_sm_annotation(new_sm_annotation, user_admin1, new_sm_post):
    """
    GIVEN a SMAnnotation model
    WHEN a new SMAnnotation is created
    THEN check the body, author, post, timestamp, id_user, and id_sm_post fields are defined correctly
    """
    assert new_sm_annotation.body == "test annotation"
    assert new_sm_annotation.author is user_admin1
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
    assert new_sm_post.id_dataset is None  # id_dataset is set by database


def test_new_sm_reply(new_sm_reply, new_sm_post):
    """
    GIVEN a SMReply model
    WHEN a new SMReply is created
    THEN check the comment, post, and id_sm_post fields are defined correctly
    """
    assert new_sm_reply.comment == "test reply"
    assert new_sm_reply.post is new_sm_post
    assert new_sm_reply.id_sm_post is None  # id_sm_post is set by database


def test_new_dataset(new_dataset, user_admin1, user_annotator1):
    """
    GIVEN a Dataset model
    WHEN a new Dataset is created
    THEN check the name, description, author, annotators, and id_author fields are defined correctly
    """
    assert new_dataset.name == "test dataset"
    assert new_dataset.description == "test description"
    assert new_dataset.author is user_admin1
    assert new_dataset.id_author is None  # id_author is set by database
    assert new_dataset.annotators[0] is user_admin1
    assert new_dataset.annotators[1] is user_annotator1


def test_roles(insert_users):
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


def test_new_psychotherapy_event(new_psychotherapy_event):
    """
    GIVEN a Psychotherapy model
    WHEN a new Psychotherapy is created
    THEN check the event_id, event_text, event_speaker, date, t_init, and c_code fields are defined correctly
    """
    assert new_psychotherapy_event.event_id == 0
    assert new_psychotherapy_event.event_text == "test event"
    assert new_psychotherapy_event.event_speaker == "test speaker"
    assert new_psychotherapy_event.date == date.today()
    assert new_psychotherapy_event.t_init == "ab"
    assert new_psychotherapy_event.c_code == "bc1234"
    assert new_psychotherapy_event.id_dataset is None  # id_dataset is set by database
