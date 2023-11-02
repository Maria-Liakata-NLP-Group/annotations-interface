from datetime import datetime, date
from app.models import (
    PSAnnotationClient,
    PSAnnotationTherapist,
    PSAnnotationDyad,
    User,
    Dataset,
    SMPost,
    SMAnnotation,
    SMReply,
    PSDialogTurn,
    PSDialogEvent,
    EvidenceClient,
    EvidenceTherapist,
    EvidenceDyad,
    ClientAnnotationSchema,
    TherapistAnnotationSchema,
    DyadAnnotationSchema,
    ClientAnnotationSchemaScale,
    AnnotationSchemaManager,
    AnnotationSchemaScaleManager,
)
from app.utils import (
    SubLabelsATherapist,
    SubLabelsADyad,
    SubLabelsBTherapist,
    SubLabelsBDyad,
    LabelStrengthBTherapist,
    LabelStrengthADyad,
    LabelNamesClient,
    LabelNamesTherapist,
    LabelNamesDyad,
)
import pytest
from sqlalchemy.exc import IntegrityError


@pytest.mark.order(1)
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


@pytest.mark.order(after="test_unique_username")
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


@pytest.mark.order(after="test_roles")
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


@pytest.mark.order(after="test_new_dataset")
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


@pytest.mark.order(after="test_new_sm_reply")
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


@pytest.mark.order(after="test_new_sm_post")
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


@pytest.mark.order(after="test_unique_email")
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


@pytest.mark.order(after="test_new_sm_annotation")
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


@pytest.mark.order(after="test_new_ps_dialog_turn")
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


@pytest.mark.order(after="test_annotation_schema_scale_manager")
def test_new_ps_annotation_client(
    db_session,
    new_ps_dialog_turn,
    new_ps_annotation_client,
):
    """
    GIVEN a PSAnnotationClient model
    WHEN a new PSAnnotationClient is created and added to the database
    THEN check its fields are defined correctly
    """
    db_session.add(new_ps_annotation_client)
    db_session.commit()

    annotation = PSAnnotationClient.query.all()[0]
    annotator1 = User.query.filter_by(username="annotator1").first()
    dataset = Dataset.query.filter_by(name="Psychotherapy Dataset Test").first()
    assert annotation.comment_summary == "test comment summary"
    assert annotation.dialog_turns.first().id == new_ps_dialog_turn.id
    assert annotation.author == annotator1
    assert annotation.dataset == dataset


@pytest.mark.order(after="test_new_ps_annotation_client")
def test_new_ps_annotation_therapist(
    db_session,
    new_ps_dialog_turn,
    new_ps_annotation_therapist,
):
    """
    GIVEN a PSAnnotationTherapist model
    WHEN a new PSAnnotationTherapist is created and added to the database
    THEN check its fields are defined correctly
    """

    db_session.add(new_ps_annotation_therapist)
    db_session.commit()

    annotation = PSAnnotationTherapist.query.all()[0]
    annotator1 = User.query.filter_by(username="annotator1").first()
    dataset = Dataset.query.filter_by(name="Psychotherapy Dataset Test").first()
    assert annotation.label_a == SubLabelsATherapist.emotional
    assert annotation.label_b == SubLabelsBTherapist.reframing
    assert annotation.strength_b == LabelStrengthBTherapist.high
    assert annotation.comment_a == "test comment a"
    assert annotation.comment_b == "test comment b"
    assert annotation.comment_summary == "test comment summary"
    assert annotation.dialog_turns.first() == new_ps_dialog_turn
    assert annotation.author == annotator1
    assert annotation.dataset == dataset


@pytest.mark.order(after="test_new_ps_annotation_therapist")
def test_new_ps_annotation_dyad(
    db_session,
    new_ps_dialog_turn,
    new_ps_annotation_dyad,
):
    """
    GIVEN a PSAnnotationDyad model
    WHEN a new PSAnnotationDyad is created and added to the database
    THEN check its fields are defined correctly
    """
    db_session.add(new_ps_annotation_dyad)
    db_session.commit()

    annotation = PSAnnotationDyad.query.all()[0]
    annotator1 = User.query.filter_by(username="annotator1").first()
    dataset = Dataset.query.filter_by(name="Psychotherapy Dataset Test").first()
    assert annotation.label_a == SubLabelsADyad.bond
    assert annotation.label_b == SubLabelsBDyad.other
    assert annotation.strength_a == LabelStrengthADyad.medium
    assert annotation.comment_a == "test comment a"
    assert annotation.comment_b == "test comment b"
    assert annotation.comment_summary == "test comment summary"
    assert annotation.dialog_turns.first() == new_ps_dialog_turn
    assert annotation.author == annotator1
    assert annotation.dataset == dataset


@pytest.mark.order(after="test_new_ps_annotation_dyad")
def test_new_evidence_client(
    db_session,
    new_evidence_client,
    new_ps_dialog_event,
    new_ps_annotation_client,
):
    """
    GIVEN a EvidenceClient model
    WHEN a new EvidenceClient is created and added to the database
    THEN check its fields are defined correctly
    """
    db_session.add(new_evidence_client)
    db_session.commit()

    evidence = EvidenceClient.query.first()
    assert evidence is not None
    assert evidence.dialog_event == new_ps_dialog_event
    assert evidence.annotation == new_ps_annotation_client
    assert evidence.label == LabelNamesClient.label_a


@pytest.mark.order(after="test_new_evidence_client")
def test_new_evidence_therapist(
    db_session,
    new_evidence_therapist,
    new_ps_dialog_event,
    new_ps_annotation_therapist,
):
    """
    GIVEN a EvidenceTherapist model
    WHEN a new EvidenceTherapist is created and added to the database
    THEN check its fields are defined correctly
    """
    db_session.add(new_evidence_therapist)
    db_session.commit()

    evidence = EvidenceTherapist.query.first()
    assert evidence is not None
    assert evidence.dialog_event == new_ps_dialog_event
    assert evidence.annotation == new_ps_annotation_therapist
    assert evidence.label == LabelNamesTherapist.label_b


@pytest.mark.order(after="test_new_evidence_therapist")
def test_new_evidence_dyad(
    db_session,
    new_evidence_dyad,
    new_ps_dialog_event,
    new_ps_annotation_dyad,
):
    """
    GIVEN a EvidenceDyad model
    WHEN a new EvidenceDyad is created and added to the database
    THEN check its fields are defined correctly
    """
    db_session.add(new_evidence_dyad)
    db_session.commit()

    evidence = EvidenceDyad.query.first()
    assert evidence is not None
    assert evidence.dialog_event == new_ps_dialog_event
    assert evidence.annotation == new_ps_annotation_dyad
    assert evidence.label == LabelNamesDyad.label_a


@pytest.mark.order(after="test_new_ps_dialog_event")
def test_new_client_annotation_schema(db_session, new_ps_annotation_client):
    """
    GIVEN a ClientAnnotationSchema model
    WHEN a new ClientAnnotationSchema is created and added to the database
    THEN check its fields are defined correctly
    """

    label_a = ClientAnnotationSchema(
        label="parent label", annotations=[new_ps_annotation_client]
    )
    label_b = ClientAnnotationSchema(
        label="child label",
        parent=label_a,
        annotations=[new_ps_annotation_client],
    )
    db_session.add_all([label_a, label_b])
    db_session.commit()

    label_a = ClientAnnotationSchema.query.filter_by(label="parent label").first()
    label_b = ClientAnnotationSchema.query.filter_by(label="child label").first()
    assert label_a.parent is None
    assert label_a.children[0] is label_b
    assert label_b.parent is label_a
    assert label_b.children.all() == []

    # verify that the annotations are correctly linked to the labels
    labels = new_ps_annotation_client.annotation_labels.all()
    assert len(labels) == 2

    with pytest.raises(IntegrityError, match="UNIQUE constraint failed"):
        """Test that a label with the same name and parent cannot be added twice"""
        label_c = ClientAnnotationSchema(label="child label", parent=label_a)
        db_session.add(label_c)
        db_session.commit()
    db_session.rollback()

    # delete the labels from the database
    db_session.delete(label_a)
    db_session.delete(label_b)
    db_session.commit()


@pytest.mark.order(after="test_new_client_annotation_schema")
def test_new_therapist_annotation_schema(db_session, new_ps_annotation_therapist):
    """
    GIVEN a TherapistAnnotationSchema model
    WHEN a new TherapistAnnotationSchema is created and added to the database
    THEN check its fields are defined correctly
    """

    label_a = TherapistAnnotationSchema(
        label="parent label", annotations=[new_ps_annotation_therapist]
    )
    label_b = TherapistAnnotationSchema(
        label="child label", parent=label_a, annotations=[new_ps_annotation_therapist]
    )
    db_session.add_all([label_a, label_b])
    db_session.commit()

    label_a = TherapistAnnotationSchema.query.filter_by(label="parent label").first()
    label_b = TherapistAnnotationSchema.query.filter_by(label="child label").first()
    assert label_a.parent is None
    assert label_a.children[0] is label_b
    assert label_b.parent is label_a
    assert label_b.children.all() == []

    # verify that the annotations are correctly linked to the labels
    labels = new_ps_annotation_therapist.annotation_labels.all()
    assert len(labels) == 2

    with pytest.raises(IntegrityError, match="UNIQUE constraint failed"):
        """Test that a label with the same name and parent cannot be added twice"""
        label_c = TherapistAnnotationSchema(label="child label", parent=label_a)
        db_session.add(label_c)
        db_session.commit()
    db_session.rollback()

    # delete the labels from the database
    db_session.delete(label_a)
    db_session.delete(label_b)
    db_session.commit()


@pytest.mark.order(after="test_new_therapist_annotation_schema")
def test_new_dyad_annotation_schema(db_session, new_ps_annotation_dyad):
    """
    GIVEN a DyadAnnotationSchema model
    WHEN a new DyadAnnotationSchema is created and added to the database
    THEN check its fields are defined correctly
    """

    label_a = DyadAnnotationSchema(
        label="parent label", annotations=[new_ps_annotation_dyad]
    )
    label_b = DyadAnnotationSchema(
        label="child label", parent=label_a, annotations=[new_ps_annotation_dyad]
    )
    db_session.add_all([label_a, label_b])
    db_session.commit()

    label_a = DyadAnnotationSchema.query.filter_by(label="parent label").first()
    label_b = DyadAnnotationSchema.query.filter_by(label="child label").first()
    assert label_a.parent is None
    assert label_a.children[0] is label_b
    assert label_b.parent is label_a
    assert label_b.children.all() == []

    # verify that the annotations are correctly linked to the labels
    labels = new_ps_annotation_dyad.annotation_labels.all()
    assert len(labels) == 2

    with pytest.raises(IntegrityError, match="UNIQUE constraint failed"):
        """Test that a label with the same name and parent cannot be added twice"""
        label_c = DyadAnnotationSchema(label="child label", parent=label_a)
        db_session.add(label_c)
        db_session.commit()
    db_session.rollback()

    # delete the labels from the database
    db_session.delete(label_a)
    db_session.delete(label_b)
    db_session.commit()


@pytest.mark.order(after="test_new_client_annotation_schema_scale")
def test_annotation_schema_manager(db_session):
    """Test the AnnotationSchemaManager class"""

    manager = AnnotationSchemaManager()
    manager.add_labels_client()

    # verify that there are 17 labels in total
    labels = ClientAnnotationSchema.query.all()
    assert len(labels) == 17
    # verify that there are only 3 labels with no parent
    assert len([label for label in labels if label.parent is None]) == 3

    # verify that "labelA1" has 2 children
    label_a1 = ClientAnnotationSchema.query.filter_by(
        label="labelA1".capitalize()
    ).first()
    assert len(label_a1.children.all()) == 2

    # verify that "labelB2" has no children
    label_b2 = ClientAnnotationSchema.query.filter_by(
        label="labelB2".capitalize()
    ).first()
    assert len(label_b2.children.all()) == 0

    # verify that the parent of "labelC4" is "labelB3"
    label_c4 = ClientAnnotationSchema.query.filter_by(
        label="labelC4".capitalize()
    ).first()
    assert label_c4.parent.label == "labelB3".capitalize()

    # verify that "labelC5" has two children, that its parent is
    # "labelB5" and that a child of "labelA2" is "labelB5"
    label_c5 = ClientAnnotationSchema.query.filter_by(
        label="labelC5".capitalize()
    ).first()
    assert len(label_c5.children.all()) == 2
    assert label_c5.parent.label == "labelB5".capitalize()
    label_b5 = ClientAnnotationSchema.query.filter_by(
        label="labelB5".capitalize()
    ).first()
    label_a2 = ClientAnnotationSchema.query.filter_by(
        label="labelA2".capitalize()
    ).first()
    assert label_b5 in label_a2.children.all()

    # verify that "labelA3" has two children and no parent
    label_a3 = ClientAnnotationSchema.query.filter_by(
        label="labelA3".capitalize()
    ).first()
    assert len(label_a3.children.all()) == 2
    assert label_a3.parent is None

    # remove the labels from the database
    manager.remove_labels_client()
    labels = ClientAnnotationSchema.query.all()
    assert len(labels) == 0


@pytest.mark.order(after="test_new_therapist_annotation_schema")
def test_new_client_annotation_schema_scale(db_session):
    """
    GIVEN a ClientAnnotationSchemaScale model
    WHEN a new ClientAnnotationSchemaScale is created and added to the database
    THEN check its fields are defined correctly
    """

    manager = AnnotationSchemaManager()
    manager.add_labels_client()
    labels = ClientAnnotationSchema.query.all()

    # find an annotation label with no parent
    label = [label for label in labels if label.parent is None][0]

    # create a scale for the label
    scale = ClientAnnotationSchemaScale(
        scale_title="scale title",
        scale_level="scale level",
        label=label,
    )
    db_session.add(scale)
    db_session.commit()

    # verify that the scale is correctly added to the database
    scale = ClientAnnotationSchemaScale.query.first()
    assert scale.scale_title == "scale title"
    assert scale.scale_level == "scale level"
    assert scale.label == label

    # verify that adding a new scale with the same title, level and label raises an exception
    with pytest.raises(IntegrityError, match="UNIQUE constraint failed"):
        scale = ClientAnnotationSchemaScale(
            scale_title="scale title",
            scale_level="scale level",
            label=label,
        )
        db_session.add(scale)
        db_session.commit()
    db_session.rollback()

    # remove the annotation labels and scales from the database
    ClientAnnotationSchemaScale.query.delete()
    db_session.commit()
    manager.remove_labels_client()
    labels = ClientAnnotationSchema.query.all()
    assert len(labels) == 0


@pytest.mark.order(after="test_annotation_schema_manager")
def test_annotation_schema_scale_manager(db_session):
    """Test the AnnotationSchemaScaleManager class"""

    schema_manager = AnnotationSchemaManager()
    schema_manager.add_labels_client()
    scales_manager = AnnotationSchemaScaleManager()
    # verify that a warning is raised if scales are added to a non-existent label
    # ("non-existent-label" in the JSON file)
    with pytest.warns(UserWarning, match="non-existent-label".strip().capitalize()):
        scales_manager.add_scales_client()

    # verify that the unique scale titles are "scale1" and "scale2"
    scales = ClientAnnotationSchemaScale.query.all()
    scale_titles = [scale.scale_title for scale in scales]
    assert set(scale_titles) == {"scale1".capitalize(), "scale2".capitalize()}

    # verify that the scales are correctly linked to the labels
    # "labelA1" has two scale titles: "scale1" and "scale2"
    label_a1 = ClientAnnotationSchema.query.filter_by(
        label="labelA1".capitalize()
    ).first()
    scale_titles = [scale.scale_title for scale in label_a1.scales.all()]
    assert scale_titles.sort() == ["scale1".capitalize(), "scale2".capitalize()].sort()
    # "labelA2" has also got two scale titles: "scale1" and "scale2"
    label_a2 = ClientAnnotationSchema.query.filter_by(
        label="labelA2".capitalize()
    ).first()
    scale_titles = [scale.scale_title for scale in label_a2.scales.all()]
    assert scale_titles.sort() == ["scale1".capitalize(), "scale2".capitalize()].sort()

    # verify that "scale1" of "labelA1" has three levels: "one", "two" and "three"
    scale1_label_a1 = ClientAnnotationSchemaScale.query.filter_by(
        scale_title="scale1".capitalize(), label=label_a1
    ).all()
    levels = [scale.scale_level for scale in scale1_label_a1]
    assert (
        levels.sort()
        == ["one".capitalize(), "two".capitalize(), "three".capitalize()].sort()
    )

    # remove scales and labels from the database
    scales_manager.remove_scales_client()
    schema_manager.remove_labels_client()
    scales = ClientAnnotationSchemaScale.query.all()
    assert len(scales) == 0
    labels = ClientAnnotationSchema.query.all()
    assert len(labels) == 0
