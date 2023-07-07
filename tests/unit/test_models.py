from datetime import datetime, date


def test_new_user(db_session, user_admin1):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check its fields are defined correctly
    """
    assert user_admin1.username == "admin1"
    assert user_admin1.email == "admin1@example.com"
    assert user_admin1.password_hash != "admin1password"
    assert user_admin1.check_password("admin1password")


def test_new_sm_annotation(new_sm_annotation, user_admin1, new_sm_post):
    """
    GIVEN a SMAnnotation model
    WHEN a new SMAnnotation is created
    THEN check its fields are defined correctly
    """
    assert new_sm_annotation.body == "test annotation"
    assert new_sm_annotation.author is user_admin1
    assert new_sm_annotation.post is new_sm_post
    assert new_sm_annotation.timestamp is None  # timestamp is set by database
    assert new_sm_annotation.id_user is None  # id_user is set by database
    assert new_sm_annotation.id_sm_post is None  # id_sm_post is set by database


def test_new_sm_post(new_sm_post, new_sm_dataset):
    """
    GIVEN a SMPost model
    WHEN a new SMPost is created
    THEN check its fields are defined correctly
    """
    assert new_sm_post.question == "test post"
    assert new_sm_post.user_id == "1"
    assert new_sm_post.timeline_id == "1"
    assert new_sm_post.post_id == 1
    assert new_sm_post.dataset is new_sm_dataset
    assert new_sm_post.id_dataset is None  # id_dataset is set by database


def test_new_sm_reply(new_sm_reply, new_sm_post, new_sm_dataset):
    """
    GIVEN a SMReply model
    WHEN a new SMReply is created
    THEN check its fields are defined correctly
    """
    assert new_sm_reply.comment == "test reply"
    assert new_sm_reply.post is new_sm_post
    assert new_sm_reply.dataset is new_sm_dataset
    assert new_sm_reply.id_sm_post is None  # id_sm_post is set by database
    assert new_sm_reply.id_dataset is None  # id_dataset is set by database


def test_new_dataset(new_sm_dataset, user_admin1, user_annotator1):
    """
    GIVEN a Dataset model
    WHEN a new Dataset is created
    THEN check its fields are defined correctly
    """
    assert new_sm_dataset.name == "Social Media Dataset Test"
    assert new_sm_dataset.description == "test description for SM dataset"
    assert new_sm_dataset.author is user_admin1
    assert new_sm_dataset.id_author is None  # id_author is set by database
    assert new_sm_dataset.annotators[0] is user_admin1
    assert new_sm_dataset.annotators[1] is user_annotator1


def test_roles(db_session):
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


def test_new_ps_dialog_turn(new_ps_dialog_turn, new_ps_dataset):
    """
    GIVEN a PSDialogTurn model
    WHEN a new PSDialogTurn is created
    THEN check its fields are defined correctly
    """
    assert new_ps_dialog_turn.c_code == "ab1234"
    assert new_ps_dialog_turn.date == date.today()
    assert (
        new_ps_dialog_turn.timestamp == datetime.strptime("00:00:00", "%H:%M:%S").time()
    )
    assert new_ps_dialog_turn.main_speaker == "Client"
    assert new_ps_dialog_turn.dataset is new_ps_dataset
    assert new_ps_dialog_turn.id_dataset is None  # id_dataset is set by database


def test_new_ps_dialog_event(new_ps_dialog_event, new_ps_dialog_turn, new_ps_dataset):
    """
    GIVEN a PSDialogEvent model
    WHEN a new PSDialogEvent is created
    THEN check its fields are defined correctly
    """
    assert new_ps_dialog_event.event_speaker == "Therapist"
    assert new_ps_dialog_event.event_plaintext == "Hello, how are you?"
    assert new_ps_dialog_event.dialog_turn is new_ps_dialog_turn
    assert new_ps_dialog_event.dataset is new_ps_dataset
    assert (
        new_ps_dialog_event.id_ps_dialog_turn is None
    )  # id_dialog_turn is set by database
    assert new_ps_dialog_event.id_dataset is None  # id_dataset is set by database
