from datetime import datetime, date
from app.models import (
    PSDialogTurnAnnotation,
    User,
    Dataset,
    SMPost,
    SMAnnotation,
    SMReply,
    PSDialogTurn,
    PSDialogEvent,
)
from app.utils import SubLabelsAClient, SubLabelsB, LabelStrength, Speaker
import pytest
from sqlalchemy.exc import IntegrityError


def test_new_user(db_session, user_admin1):
    """
    GIVEN a User model
    WHEN a new User is created and added to the database
    THEN check its fields are defined correctly
    """
    db_session.add(user_admin1)
    db_session.commit()
    user = User.query.filter_by(username="admin1").first()
    assert user.username == "admin1"
    assert user.email == "admin1@example.com"
    assert user.password_hash != "admin1password"
    assert user.check_password("admin1password")


@pytest.mark.order(after="test_new_user")
def test_unique_username(db_session):
    """
    GIVEN a User model
    WHEN a new User is created with an existing username in the database
    THEN check that an exception is raised
    """
    user = User(username="admin1", email="test@example.com")
    user.set_password("testpassword")
    db_session.add(user)
    # test that an exception is raised
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


@pytest.mark.order(after="test_new_user")
def test_unique_email(db_session):
    """
    GIVEN a User model
    WHEN a new User is created with an existing email in the database
    THEN check that an exception is raised
    """
    user = User(username="test", email="admin1@example.com")
    user.set_password("testpassword")
    db_session.add(user)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_new_dataset(db_session, new_sm_dataset):
    """
    GIVEN a Dataset model
    WHEN a new Dataset is created and added to the database
    THEN check its fields are defined correctly
    """
    db_session.add(new_sm_dataset)
    db_session.commit()
    admin1 = User.query.filter_by(username="admin1").first()
    annotator1 = User.query.filter_by(username="annotator1").first()
    dataset = Dataset.query.filter_by(name="Social Media Dataset Test").first()
    assert dataset.name == "Social Media Dataset Test"
    assert dataset.description == "test description for SM dataset"
    assert dataset.author is admin1
    assert dataset.id_author is admin1.id
    assert dataset.annotators[0] is admin1
    assert dataset.annotators[1] is annotator1


def test_new_sm_post(db_session, new_sm_post):
    """
    GIVEN a SMPost model
    WHEN a new SMPost is created and added to the database
    THEN check its fields are defined correctly
    """
    db_session.add(new_sm_post)
    db_session.commit()
    sm_post = SMPost.query.filter_by(question="test post").first()
    sm_dataset = Dataset.query.filter_by(name="Social Media Dataset Test").first()
    assert sm_post.question == "test post"
    assert sm_post.user_id == "1"
    assert sm_post.timeline_id == "1"
    assert sm_post.post_id == 1
    assert sm_post.dataset is sm_dataset
    assert sm_post.id_dataset is sm_dataset.id


def test_new_sm_annotation(db_session, new_sm_annotation):
    """
    GIVEN a SMAnnotation model
    WHEN a new SMAnnotation is created and added to the database
    THEN check its fields are defined correctly
    """
    db_session.add(new_sm_annotation)
    db_session.commit()
    sm_annotation = SMAnnotation.query.filter_by(body="test annotation").first()
    admin1 = User.query.filter_by(username="admin1").first()
    sm_post = SMPost.query.filter_by(question="test post").first()
    assert sm_annotation.body == "test annotation"
    assert sm_annotation.author is admin1
    assert sm_annotation.post is sm_post
    assert sm_annotation.id_user is admin1.id
    assert sm_annotation.id_sm_post is sm_post.id


def test_new_sm_reply(db_session, new_sm_reply):
    """
    GIVEN a SMReply model
    WHEN a new SMReply is created and added to the database
    THEN check its fields are defined correctly
    """
    db_session.add(new_sm_reply)
    db_session.commit()
    sm_reply = SMReply.query.filter_by(comment="test reply").first()
    sm_post = SMPost.query.filter_by(question="test post").first()
    sm_dataset = Dataset.query.filter_by(name="Social Media Dataset Test").first()
    assert sm_reply.comment == "test reply"
    assert sm_reply.post is sm_post
    assert sm_reply.dataset is sm_dataset
    assert sm_reply.id_sm_post is sm_post.id
    assert sm_reply.id_dataset is sm_dataset.id


def test_roles(db_session):
    """
    GIVEN a Role model
    WHEN a new Role is created and added to the database
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


def test_new_ps_dialog_turn(db_session, new_ps_dialog_turn):
    """
    GIVEN a PSDialogTurn model
    WHEN a new PSDialogTurn is created and added to the database
    THEN check its fields are defined correctly
    """
    db_session.add(new_ps_dialog_turn)
    db_session.commit()
    ps_dialog_turn = PSDialogTurn.query.all()[0]
    ps_dataset = Dataset.query.filter_by(name="Psychotherapy Dataset Test").first()
    assert ps_dialog_turn.c_code == "ab1234"
    assert ps_dialog_turn.date == date.today()
    assert ps_dialog_turn.timestamp == datetime.strptime("00:00:00", "%H:%M:%S").time()
    assert ps_dialog_turn.main_speaker == "Client"
    assert ps_dialog_turn.dataset is ps_dataset
    assert ps_dialog_turn.id_dataset is ps_dataset.id


def test_new_ps_dialog_event(db_session, new_ps_dialog_event):
    """
    GIVEN a PSDialogEvent model
    WHEN a new PSDialogEvent is created and added to the database
    THEN check its fields are defined correctly
    """
    db_session.add(new_ps_dialog_event)
    db_session.commit()
    ps_dialog_event = PSDialogEvent.query.all()[0]
    ps_dialog_turn = PSDialogTurn.query.all()[0]
    ps_dataset = Dataset.query.filter_by(name="Psychotherapy Dataset Test").first()
    assert ps_dialog_event.event_n == 1
    assert ps_dialog_event.event_speaker == "Therapist"
    assert ps_dialog_event.event_plaintext == "Hello, how are you?"
    assert ps_dialog_event.dialog_turn is ps_dialog_turn
    assert ps_dialog_event.dataset is ps_dataset
    assert ps_dialog_event.id_ps_dialog_turn is ps_dialog_turn.id
    assert ps_dialog_event.id_dataset is ps_dataset.id


def test_new_ps_dialog_turn_annotation(
    db_session,
    new_ps_dialog_turn,
    new_ps_dialog_turn_annotation,
):
    """
    GIVEN a PSDialogTurnAnnotation model
    WHEN a new PSDialogTurnAnnotation is created and added to the database
    THEN check its fields are defined correctly
    """
    db_session.add(new_ps_dialog_turn_annotation)
    db_session.commit()

    annotation = PSDialogTurnAnnotation.query.all()[0]
    annotator1 = User.query.filter_by(username="annotator1").first()
    dataset = Dataset.query.filter_by(name="Psychotherapy Dataset Test").first()
    assert annotation.label_a_client == SubLabelsAClient.attachment
    assert annotation.label_b == SubLabelsB.sublabel2
    assert annotation.strength_a == LabelStrength.low
    assert annotation.strength_b == LabelStrength.medium
    assert annotation.speaker == Speaker.client
    assert annotation.dialog_turn == new_ps_dialog_turn
    assert annotation.author == annotator1
    assert annotation.dataset == dataset
