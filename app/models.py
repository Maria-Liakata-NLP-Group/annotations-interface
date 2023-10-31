from app import db, login
from datetime import datetime, date
import json
from typing import Union
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
import warnings
import os
from app.utils import (
    SMAnnotationType,
    DatasetType,
    Permission,
    SubLabelsAClient,
    SubLabelsATherapist,
    SubLabelsADyad,
    SubLabelsBClient,
    SubLabelsBTherapist,
    SubLabelsBDyad,
    SubLabelsCClient,
    SubLabelsCTherapist,
    SubLabelsDClient,
    SubLabelsDTherapist,
    SubLabelsEClient,
    SubLabelsETherapist,
    SubLabelsFClient,
    LabelStrengthAClient,
    LabelStrengthATherapist,
    LabelStrengthADyad,
    LabelStrengthBClient,
    LabelStrengthBTherapist,
    LabelStrengthBDyad,
    LabelStrengthCClient,
    LabelStrengthCTherapist,
    LabelStrengthDClient,
    LabelStrengthDTherapist,
    LabelStrengthETherapist,
    LabelStrengthEClient,
    LabelStrengthFClient,
    LabelNamesClient,
    LabelNamesTherapist,
    LabelNamesDyad,
)


@login.user_loader
def load_user(id):
    """Load user from database. Used by flask_login."""
    return User.query.get(int(id))


# association table for many-to-many relationship between User and Dataset
dataset_annotator = db.Table(
    "dataset_annotator",
    db.Column("id_dataset", db.Integer, db.ForeignKey("dataset.id")),
    db.Column("id_annotator", db.Integer, db.ForeignKey("user.id")),
)


# association table for many-to-many relationship between PSDialogTurn and PSAnnotationClient
annotationclient_dialogturn = db.Table(
    "annotationclient_dialogturn",
    db.Column("id_dialog_turn", db.Integer, db.ForeignKey("ps_dialog_turn.id")),
    db.Column(
        "id_annotation_client",
        db.Integer,
        db.ForeignKey("ps_annotation_client.id"),
    ),
)


# association table for many-to-many relationship between PSDialogTurn and PSAnnotationTherapist
annotationtherapist_dialogturn = db.Table(
    "annotationtherapist_dialogturn",
    db.Column("id_dialog_turn", db.Integer, db.ForeignKey("ps_dialog_turn.id")),
    db.Column(
        "id_annotation_therapist",
        db.Integer,
        db.ForeignKey("ps_annotation_therapist.id"),
    ),
)

# association table for many-to-many relationship between PSDialogTurn and PSAnnotationDyad
annotationsdyad_dialogturn = db.Table(
    "annotationsdyad_dialogturn",
    db.Column("id_dialog_turn", db.Integer, db.ForeignKey("ps_dialog_turn.id")),
    db.Column(
        "id_annotation_dyad",
        db.Integer,
        db.ForeignKey("ps_annotation_dyad.id"),
    ),
)


# association table for many-to-many relationship between ClientAnnotationSchema and PSAnnotationClient
annotationclient_annotationschema = db.Table(
    "annotationclient_annotationschema",
    db.Column(
        "id_ps_annotation_client",
        db.Integer,
        db.ForeignKey("ps_annotation_client.id"),
    ),
    db.Column(
        "id_client_annotation_schema",
        db.Integer,
        db.ForeignKey("client_annotation_schema.id"),
    ),
)


# association table for many-to-many relationship between TherapistAnnotationSchema and PSAnnotationTherapist
annotationtherapist_annotationschema = db.Table(
    "annotationtherapist_annotationschema",
    db.Column(
        "id_ps_annotation_therapist",
        db.Integer,
        db.ForeignKey("ps_annotation_therapist.id"),
    ),
    db.Column(
        "id_therapist_annotation_schema",
        db.Integer,
        db.ForeignKey("therapist_annotation_schema.id"),
    ),
)


# association table for many-to-many relationship between DyadAnnotationSchema and PSAnnotationDyad
annotationdyad_annotationschema = db.Table(
    "annotationdyad_annotationschema",
    db.Column(
        "id_ps_annotation_dyad",
        db.Integer,
        db.ForeignKey("ps_annotation_dyad.id"),
    ),
    db.Column(
        "id_dyad_annotation_schema",
        db.Integer,
        db.ForeignKey("dyad_annotation_schema.id"),
    ),
)


class User(UserMixin, db.Model):
    """User class for database"""

    id = db.Column(db.Integer, primary_key=True)  # each user will have unique id
    username = db.Column(
        db.String(64), index=True, unique=True
    )  # index=True - for faster search
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))  # hash of password
    id_role = db.Column(db.Integer, db.ForeignKey("role.id"))  # id of user's role
    annotations_sm = db.relationship(
        "SMAnnotation", backref="author", lazy="dynamic"
    )  # one-to-many relationship with SMAnnotation class
    annotations_client = db.relationship(
        "PSAnnotationClient", backref="author", lazy="dynamic"
    )  # one-to-many relationship with PSAnnotationClient class
    annotations_therapist = db.relationship(
        "PSAnnotationTherapist", backref="author", lazy="dynamic"
    )  # one-to-many relationship with PSAnnotationTherapist class
    annotations_dyad = db.relationship(
        "PSAnnotationDyad", backref="author", lazy="dynamic"
    )  # one-to-many relationship with PSAnnotationDyad class
    authored_datasets = db.relationship(
        "Dataset",
        backref="author",
        lazy="dynamic",
        foreign_keys="Dataset.id_author",
    )  # one-to-many relationship with Dataset class

    def __repr__(self):
        """How to print objects of this class"""
        return "<User {}>".format(self.username)

    def set_password(self, password):
        """Set password for user"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password is correct"""
        return check_password_hash(self.password_hash, password)

    def __init__(self, **kwargs):
        """Initialize user. If role is not provided, set it to default role."""
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email in current_app.config["APP_ADMIN"]:
                # if user is admin, set role to Administrator
                self.role = Role.query.filter_by(name="Administrator").first()
            if self.role is None:
                # if user is not admin, set role to default role
                self.role = Role.query.filter_by(default=True).first()

    def can(self, perm):
        """Check if user has permission"""
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        """Check if user is administrator"""
        return self.can(Permission.ADMIN)


class AnonymousUser(AnonymousUserMixin):
    """
    Anonymous user class for flask_login. Used when user is not logged in.
    """

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login.anonymous_user = AnonymousUser  # set anonymous user class


class Role(db.Model):
    """Role class for database"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)  # name of role
    default = db.Column(
        db.Boolean, default=False, index=True
    )  # default role assigned to new users
    permissions = db.Column(db.Integer)  # permissions for this role
    users = db.relationship(
        "User", backref="role", lazy="dynamic"
    )  # one-to-many relationship with User class

    def __init__(self, **kwargs):
        """
        Initialize role.
        If permissions are not provided, set them to 0.
        """
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    # static method to insert roles into database,
    # instead of creating them manually
    @staticmethod
    def insert_roles():
        """
        Insert roles into database.
        To create new role, add it to roles dictionary.
        """
        roles = {
            "Annotator": [Permission.READ, Permission.WRITE],
            "Administrator": [Permission.READ, Permission.WRITE, Permission.ADMIN],
        }
        default_role = "Annotator"
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = role.name == default_role
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        """How to print objects of this class"""
        return "<Role {}>".format(self.name)


class SMAnnotation(db.Model):
    """Social Media Annotation class for database"""

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(SMAnnotationType), nullable=True)  # type of annotation
    body = db.Column(db.Text)  # annotation body
    timestamp = db.Column(
        db.DateTime, index=True, default=datetime.utcnow
    )  # when annotation was created
    id_user = db.Column(
        db.Integer, db.ForeignKey("user.id")
    )  # id of user who created this annotation
    id_sm_post = db.Column(
        db.Integer, db.ForeignKey("sm_post.id")
    )  # id of post which is annotated

    def __repr__(self):
        """How to print objects of this class"""
        return "<Social Media Annotation {}>".format(self.body)


class SMPost(db.Model):
    """Social Media Post class for database"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), index=True, unique=False)
    timeline_id = db.Column(db.String(64), index=True, unique=False)
    post_id = db.Column(db.Integer, index=True, unique=False)
    mood = db.Column(db.String(64))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    ldate = db.Column(db.DateTime, default=datetime.utcnow)
    question = db.Column(db.Text)
    id_dataset = db.Column(db.Integer, db.ForeignKey("dataset.id"))
    annotations = db.relationship(
        "SMAnnotation", backref="post", lazy="dynamic"
    )  # one-to-many relationship with SMAnnotation class
    replies = db.relationship(
        "SMReply", backref="post", lazy="dynamic"
    )  # one-to-many relationship with SMReply class

    def __repr__(self):
        """How to print objects of this class"""
        return "<Social Media Post {}>".format(self.question)


class SMReply(db.Model):
    """Social Media Reply class for database"""

    id = db.Column(db.Integer, primary_key=True)
    reply_id = db.Column(db.Integer, index=True, unique=False)
    user_id = db.Column(db.String(64), index=True, unique=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    ldate = db.Column(db.DateTime, default=datetime.utcnow)
    comment = db.Column(db.Text)
    id_sm_post = db.Column(db.Integer, db.ForeignKey("sm_post.id"))
    id_dataset = db.Column(db.Integer, db.ForeignKey("dataset.id"))

    def __repr__(self):
        """How to print objects of this class"""
        return "<Social Media Reply {}>".format(self.comment)


class Dataset(db.Model):
    """Dataset class for database"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=False)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.Enum(DatasetType), nullable=True)  # type of dataset
    id_author = db.Column(
        db.Integer, db.ForeignKey("user.id")
    )  # id of user who created this dataset
    annotators = db.relationship(
        "User",
        secondary=dataset_annotator,
        backref=db.backref("datasets", lazy="dynamic"),
        lazy="dynamic",
    )  # many-to-many relationship with User class
    posts = db.relationship(
        "SMPost", backref="dataset", lazy="dynamic"
    )  # one-to-many relationship with SMPost class
    replies = db.relationship(
        "SMReply", backref="dataset", lazy="dynamic"
    )  # one-to-many relationship with SMReply class
    dialog_turns = db.relationship(
        "PSDialogTurn", backref="dataset", lazy="dynamic"
    )  # one-to-many relationship with PSDialogTurn class
    dialog_events = db.relationship(
        "PSDialogEvent", backref="dataset", lazy="dynamic"
    )  # one-to-many relationship with PSDialogEvent class
    annotations_client = db.relationship(
        "PSAnnotationClient", backref="dataset", lazy="dynamic"
    )  # one-to-many relationship with PSAnnotationClient class
    annotations_therapist = db.relationship(
        "PSAnnotationTherapist", backref="dataset", lazy="dynamic"
    )  # one-to-many relationship with PSAnnotationTherapist class
    annotations_dyad = db.relationship(
        "PSAnnotationDyad", backref="dataset", lazy="dynamic"
    )  # one-to-many relationship with PSAnnotationDyad class

    def __repr__(self):
        """How to print objects of this class"""
        return "<Dataset {}>".format(self.name)


class PSDialogTurn(db.Model):
    """
    Psychotherapy Dialog Turn class for database
    Each row is a different dialog turn in a psychotherapy session
    A dialog turn is composed of one or more events (speech turns by therapist, client or annotator)
    The start of a dialog turn is identified by a "timestamp" event in the dataset
    """

    __tablename__ = "ps_dialog_turn"
    id = db.Column(db.Integer, primary_key=True)
    c_code = db.Column(db.String(64), index=True, unique=False)  # patient ID
    t_init = db.Column(db.String(64), default=None)  # therapist initials
    date = db.Column(db.Date, default=date.today)  # date of session
    # the timestamp is the time measured from the start of the session
    timestamp = db.Column(
        db.Time, default=datetime.strptime("00:00:00", "%H:%M:%S").time()
    )
    main_speaker = db.Column(
        db.String(64)
    )  # one of 'Therapist', 'Client' or 'Annotator'
    session_n = db.Column(db.Integer)  # session number
    dialog_turn_n = db.Column(db.Integer)  # dialog turn number
    id_dataset = db.Column(
        db.Integer, db.ForeignKey("dataset.id")
    )  # id of dataset associated with this dialog turn
    dialog_events = db.relationship(
        "PSDialogEvent", backref="dialog_turn", lazy="dynamic"
    )  # one-to-many relationship with PSDialogEvent class


class PSDialogEvent(db.Model):
    """
    Psychotherapy Dialog Event class for database
    Each row is a different dialog event in a psychotherapy session
    A dialog event is a speech turn by therapist, client or annotator
    """

    __tablename__ = "ps_dialog_event"
    id = db.Column(db.Integer, primary_key=True)
    event_n = db.Column(db.Integer)  # event number
    event_speaker = db.Column(
        db.String(64)
    )  # one of 'Therapist', 'Client' or 'Annotator
    event_plaintext = db.Column(db.Text)  # speech turn
    id_ps_dialog_turn = db.Column(
        db.Integer, db.ForeignKey("ps_dialog_turn.id")
    )  # id of dialog turn
    id_dataset = db.Column(
        db.Integer, db.ForeignKey("dataset.id")
    )  # id of dataset associated with this dialog event
    evidence_client = db.relationship(
        "EvidenceClient", backref="dialog_event", lazy="dynamic"
    )  # one-to-many relationship with EvidenceClient class
    evidence_therapist = db.relationship(
        "EvidenceTherapist", backref="dialog_event", lazy="dynamic"
    )  # one-to-many relationship with EvidenceTherapist class
    evidence_dyad = db.relationship(
        "EvidenceDyad", backref="dialog_event", lazy="dynamic"
    )  # one-to-many relationship with EvidenceDyad class


class PSAnnotationClient(db.Model):
    """
    Psychotherapy Dialog Turn Annotation class for the Client.
    This captures annotations of psychotherapy sessions for the client at the 'segment' level.
    """

    __tablename__ = "ps_annotation_client"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.DateTime, index=True, default=datetime.utcnow
    )  # when annotation was created
    label_a = db.Column(db.Enum(SubLabelsAClient), nullable=True, default=None)
    label_b = db.Column(db.Enum(SubLabelsBClient), nullable=True, default=None)
    label_c = db.Column(db.Enum(SubLabelsCClient), nullable=True, default=None)
    label_d = db.Column(db.Enum(SubLabelsDClient), nullable=True, default=None)
    label_e = db.Column(db.Enum(SubLabelsEClient), nullable=True, default=None)
    label_f = db.Column(db.Enum(SubLabelsFClient), nullable=True, default=None)
    strength_a = db.Column(db.Enum(LabelStrengthAClient), nullable=True, default=None)
    strength_b = db.Column(db.Enum(LabelStrengthBClient), nullable=True, default=None)
    strength_c = db.Column(db.Enum(LabelStrengthCClient), nullable=True, default=None)
    strength_d = db.Column(db.Enum(LabelStrengthDClient), nullable=True, default=None)
    strength_e = db.Column(db.Enum(LabelStrengthEClient), nullable=True, default=None)
    strength_f = db.Column(db.Enum(LabelStrengthFClient), nullable=True, default=None)
    comment_a = db.Column(db.Text, nullable=True)
    comment_b = db.Column(db.Text, nullable=True)
    comment_c = db.Column(db.Text, nullable=True)
    comment_d = db.Column(db.Text, nullable=True)
    comment_e = db.Column(db.Text, nullable=True)
    comment_f = db.Column(db.Text, nullable=True)
    comment_summary = db.Column(db.Text, nullable=True)
    dialog_turns = db.relationship(
        "PSDialogTurn",
        secondary=annotationclient_dialogturn,
        backref=db.backref("annotations_client", lazy="dynamic"),
        lazy="dynamic",
    )  # many-to-many relationship with PSDialogTurn class
    id_user = db.Column(
        db.Integer, db.ForeignKey("user.id")
    )  # id of user (annotator) who created this annotation
    id_dataset = db.Column(
        db.Integer, db.ForeignKey("dataset.id")
    )  # id of dataset associated with this annotation
    evidence = db.relationship(
        "EvidenceClient", backref="annotation", lazy="dynamic"
    )  # one-to-many relationship with EvidenceClient class
    # many-to-many relationship with ClientAnnotationSchema class
    annotation_labels = db.relationship(
        "ClientAnnotationSchema",
        secondary=annotationclient_annotationschema,
        backref=db.backref("annotations", lazy="dynamic"),
        lazy="dynamic",
    )


class PSAnnotationTherapist(db.Model):
    """
    Psychotherapy Dialog Turn Annotation class for the Therapist.
    This captures annotations of psychotherapy sessions for the therapist at the 'segment' level.
    """

    __tablename__ = "ps_annotation_therapist"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.DateTime, index=True, default=datetime.utcnow
    )  # when annotation was created
    label_a = db.Column(db.Enum(SubLabelsATherapist), nullable=True, default=None)
    label_b = db.Column(db.Enum(SubLabelsBTherapist), nullable=True, default=None)
    label_c = db.Column(db.Enum(SubLabelsCTherapist), nullable=True, default=None)
    label_d = db.Column(db.Enum(SubLabelsDTherapist), nullable=True, default=None)
    label_e = db.Column(db.Enum(SubLabelsETherapist), nullable=True, default=None)
    strength_a = db.Column(
        db.Enum(LabelStrengthATherapist), nullable=True, default=None
    )
    strength_b = db.Column(
        db.Enum(LabelStrengthBTherapist), nullable=True, default=None
    )
    strength_c = db.Column(
        db.Enum(LabelStrengthCTherapist), nullable=True, default=None
    )
    strength_d = db.Column(
        db.Enum(LabelStrengthDTherapist), nullable=True, default=None
    )
    strength_e = db.Column(
        db.Enum(LabelStrengthETherapist), nullable=True, default=None
    )
    comment_a = db.Column(db.Text, nullable=True)
    comment_b = db.Column(db.Text, nullable=True)
    comment_c = db.Column(db.Text, nullable=True)
    comment_d = db.Column(db.Text, nullable=True)
    comment_e = db.Column(db.Text, nullable=True)
    comment_summary = db.Column(db.Text, nullable=True)
    dialog_turns = db.relationship(
        "PSDialogTurn",
        secondary=annotationtherapist_dialogturn,
        backref=db.backref("annotations_therapist", lazy="dynamic"),
        lazy="dynamic",
    )  # many-to-many relationship with PSDialogTurn class
    id_user = db.Column(
        db.Integer, db.ForeignKey("user.id")
    )  # id of user (annotator) who created this annotation
    id_dataset = db.Column(
        db.Integer, db.ForeignKey("dataset.id")
    )  # id of dataset associated with this annotation
    evidence = db.relationship(
        "EvidenceTherapist", backref="annotation", lazy="dynamic"
    )  # one-to-many relationship with EvidenceTherapist class
    # many-to-many relationship with TherapistAnnotationSchema class
    annotation_labels = db.relationship(
        "TherapistAnnotationSchema",
        secondary=annotationtherapist_annotationschema,
        backref=db.backref("annotations", lazy="dynamic"),
        lazy="dynamic",
    )


class PSAnnotationDyad(db.Model):
    """
    Psychotherapy Dialog Turn Annotation class for the Dyad.
    This captures annotations of psychotherapy sessions for the dyad at the 'segment' level.
    """

    __tablename__ = "ps_annotation_dyad"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.DateTime, index=True, default=datetime.utcnow
    )  # when annotation was created
    label_a = db.Column(db.Enum(SubLabelsADyad), nullable=True, default=None)
    label_b = db.Column(db.Enum(SubLabelsBDyad), nullable=True, default=None)
    strength_a = db.Column(db.Enum(LabelStrengthADyad), nullable=True, default=None)
    strength_b = db.Column(db.Enum(LabelStrengthBDyad), nullable=True, default=None)
    comment_a = db.Column(db.Text, nullable=True)
    comment_b = db.Column(db.Text, nullable=True)
    comment_summary = db.Column(db.Text, nullable=True)
    dialog_turns = db.relationship(
        "PSDialogTurn",
        secondary=annotationsdyad_dialogturn,
        backref=db.backref("annotations_dyad", lazy="dynamic"),
        lazy="dynamic",
    )  # many-to-many relationship with PSDialogTurn class
    id_user = db.Column(
        db.Integer, db.ForeignKey("user.id")
    )  # id of user (annotator) who created this annotation
    id_dataset = db.Column(
        db.Integer, db.ForeignKey("dataset.id")
    )  # id of dataset associated with this annotation
    evidence = db.relationship(
        "EvidenceDyad", backref="annotation", lazy="dynamic"
    )  # one-to-many relationship with EvidenceDyad class
    # many-to-many relationship with DyadAnnotationSchema class
    annotation_labels = db.relationship(
        "DyadAnnotationSchema",
        secondary=annotationdyad_annotationschema,
        backref=db.backref("annotations", lazy="dynamic"),
        lazy="dynamic",
    )


class EvidenceClient(db.Model):
    """Table to store the dialog events that are marked as evidence for a particular annotation for the client"""

    __tablename__ = "evidence_client"
    id = db.Column(db.Integer, primary_key=True)
    id_ps_dialog_event = db.Column(db.Integer, db.ForeignKey("ps_dialog_event.id"))
    id_ps_annotation_client = db.Column(
        db.Integer, db.ForeignKey("ps_annotation_client.id")
    )
    label = db.Column(db.Enum(LabelNamesClient), nullable=True, default=None)


class EvidenceTherapist(db.Model):
    """Table to store the dialog events that are marked as evidence for a particular annotation for the therapist"""

    __tablename__ = "evidence_therapist"
    id = db.Column(db.Integer, primary_key=True)
    id_ps_dialog_event = db.Column(db.Integer, db.ForeignKey("ps_dialog_event.id"))
    id_ps_annotation_therapist = db.Column(
        db.Integer, db.ForeignKey("ps_annotation_therapist.id")
    )
    label = db.Column(db.Enum(LabelNamesTherapist), nullable=True, default=None)


class EvidenceDyad(db.Model):
    """Table to store the dialog events that are marked as evidence for a particular annotation for the dyad"""

    __tablename__ = "evidence_dyad"
    id = db.Column(db.Integer, primary_key=True)
    id_ps_dialog_event = db.Column(db.Integer, db.ForeignKey("ps_dialog_event.id"))
    id_ps_annotation_dyad = db.Column(
        db.Integer, db.ForeignKey("ps_annotation_dyad.id")
    )
    label = db.Column(db.Enum(LabelNamesDyad), nullable=True, default=None)


class ClientAnnotationSchema(db.Model):
    """Self-referencing table to store the client annotation schema"""

    __tablename__ = "client_annotation_schema"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64), index=True, nullable=False)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("client_annotation_schema.id"), default=None
    )
    children = db.relationship(
        "ClientAnnotationSchema",
        backref=db.backref("parent", remote_side=[id]),
        lazy="dynamic",
    )
    scales = db.relationship(
        "ClientAnnotationSchemaScale",
        backref="label",
        lazy="dynamic",
    )  # one-to-many relationship with ClientAnnotationSchemaScale class
    # create unique constraint on label within a parent
    __table_args__ = (db.UniqueConstraint("label", "parent_id"),)

    def __repr__(self):
        """How to print objects of this class"""
        return "<ClientAnnotationSchema {}>".format(self.label[:10])


class TherapistAnnotationSchema(db.Model):
    """Self-referencing table to store the therapist annotation schema"""

    __tablename__ = "therapist_annotation_schema"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64), index=True, nullable=False)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("therapist_annotation_schema.id"), default=None
    )
    children = db.relationship(
        "TherapistAnnotationSchema",
        backref=db.backref("parent", remote_side=[id]),
        lazy="dynamic",
    )
    scales = db.relationship(
        "TherapistAnnotationSchemaScale",
        backref="label",
        lazy="dynamic",
    )  # one-to-many relationship with TherapistAnnotationSchemaScale class

    # create unique constraint on label within a parent
    __table_args__ = (db.UniqueConstraint("label", "parent_id"),)

    def __repr__(self):
        """How to print objects of this class"""
        return "<TherapistAnnotationSchema {}>".format(self.label[:10])


class DyadAnnotationSchema(db.Model):
    """Self-referencing table to store the dyad annotation schema"""

    __tablename__ = "dyad_annotation_schema"
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64), index=True, nullable=False)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("dyad_annotation_schema.id"), default=None
    )
    children = db.relationship(
        "DyadAnnotationSchema",
        backref=db.backref("parent", remote_side=[id]),
        lazy="dynamic",
    )
    scales = db.relationship(
        "DyadAnnotationSchemaScale",
        backref="label",
        lazy="dynamic",
    )  # one-to-many relationship with DyadAnnotationSchemaScale class
    # create unique constraint on label within a parent
    __table_args__ = (db.UniqueConstraint("label", "parent_id"),)

    def __repr__(self):
        """How to print objects of this class"""
        return "<DyadAnnotationSchema {}>".format(self.label[:10])


class ClientAnnotationSchemaScale(db.Model):
    """Table to store the scales for the client annotation schema"""

    __tablename__ = "client_annotation_schema_scale"

    id = db.Column(db.Integer, primary_key=True)
    scale_title = db.Column(db.String(64), index=True, nullable=False)
    scale_level = db.Column(db.String(64), index=True, nullable=False)
    id_client_annotation_schema = db.Column(
        db.Integer, db.ForeignKey("client_annotation_schema.id")
    )
    # create unique constraint on scale_title, scale_level and id_client_annotation_schema
    __table_args__ = (
        db.UniqueConstraint(
            "scale_title", "scale_level", "id_client_annotation_schema"
        ),
    )

    def __repr__(self):
        """How to print objects of this class"""
        return "<ClientAnnotationSchemaScale {}>".format(self.scale_title[:10])


class TherapistAnnotationSchemaScale(db.Model):
    """Table to store the scales for the therapist annotation schema"""

    __tablename__ = "therapist_annotation_schema_scale"

    id = db.Column(db.Integer, primary_key=True)
    scale_title = db.Column(db.String(64), index=True, nullable=False)
    scale_level = db.Column(db.String(64), index=True, nullable=False)
    id_therapist_annotation_schema = db.Column(
        db.Integer, db.ForeignKey("therapist_annotation_schema.id")
    )
    # create unique constraint on scale_title, scale_level and id_therapist_annotation_schema
    __table_args__ = (
        db.UniqueConstraint(
            "scale_title", "scale_level", "id_therapist_annotation_schema"
        ),
    )

    def __repr__(self):
        """How to print objects of this class"""
        return "<TherapistAnnotationSchemaScale {}>".format(self.scale_title[:10])


class DyadAnnotationSchemaScale(db.Model):
    """Table to store the scales for the dyad annotation schema"""

    __tablename__ = "dyad_annotation_schema_scale"

    id = db.Column(db.Integer, primary_key=True)
    scale_title = db.Column(db.String(64), index=True, nullable=False)
    scale_level = db.Column(db.String(64), index=True, nullable=False)
    id_dyad_annotation_schema = db.Column(
        db.Integer, db.ForeignKey("dyad_annotation_schema.id")
    )
    # create unique constraint on scale_title, scale_level and id_dyad_annotation_schema
    __table_args__ = (
        db.UniqueConstraint("scale_title", "scale_level", "id_dyad_annotation_schema"),
    )

    def __repr__(self):
        """How to print objects of this class"""
        return "<DyadAnnotationSchemaScale {}>".format(self.scale_title[:10])


class AnnotationSchemaManager:
    def __init__(self):
        """Initialize the manager specifying the JSON files containing the annotation schema"""
        self.filename_client = os.path.join(
            current_app.config["ANNOTATION_SCHEMA_PATH"], "client.json"
        )
        self.filename_therapist = os.path.join(
            current_app.config["ANNOTATION_SCHEMA_PATH"], "therapist.json"
        )
        self.filename_dyad = os.path.join(
            current_app.config["ANNOTATION_SCHEMA_PATH"], "dyad.json"
        )

    def _read_json(self, filename: str):
        """Read the JSON file"""
        with open(filename, "r") as f:
            data = json.load(f)
        return data

    def _add_labels(
        self,
        annotation_schema_model: Union[
            ClientAnnotationSchema, TherapistAnnotationSchema, DyadAnnotationSchema
        ],
        filename: str,
    ):
        """
        Add annotation labels to the database.

        Parameters
        ----------
        annotation_schema_model : ClientAnnotationSchema or TherapistAnnotationSchema or DyadAnnotationSchema
            The annotation schema model class for the client, therapist or dyad
        filename : str
            The path to the JSON file containing the annotation schema
        """
        schema = self._read_json(filename)  # read the annotation schema

        def add_labels_recursive(label_data: dict, parent_label=None, labels=[]):
            """
            Recursively add labels to the database session.
            Note the labels are stripped of leading and trailing whitespace and capitalized.
            """

            for label_name, children in label_data.items():
                label_name = label_name.strip().capitalize()
                label = annotation_schema_model(label=label_name, parent=parent_label)
                labels.append(label)
                if isinstance(children, dict):
                    add_labels_recursive(children, parent_label=label, labels=labels)
                elif isinstance(children, list) and len(children) > 0:
                    for child in children:
                        child = child.strip().capitalize()
                        labels.append(
                            annotation_schema_model(label=child, parent=label)
                        )
            db.session.add_all(labels)

        try:
            add_labels_recursive(schema)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            raise e

        return None

    def _remove_labels(
        self,
        annotation_schema_model: Union[
            ClientAnnotationSchema, TherapistAnnotationSchema, DyadAnnotationSchema
        ],
    ):
        """
        Remove all annotation labels for the client, therapist or dyad from the database.

        Parameters
        ----------
        annotation_schema_model : ClientAnnotationSchema or TherapistAnnotationSchema or DyadAnnotationSchema
            The annotation schema model class for the client, therapist or dyad
        """
        try:
            annotation_schema_model.query.delete()
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            raise e

        return None

    def add_labels_client(self):
        """Add annotation labels for the client to the database"""
        return self._add_labels(ClientAnnotationSchema, self.filename_client)

    def add_labels_therapist(self):
        """Add annotation labels for the therapist to the database"""
        return self._add_labels(TherapistAnnotationSchema, self.filename_therapist)

    def add_labels_dyad(self):
        """Add annotation labels for the dyad to the database"""
        return self._add_labels(DyadAnnotationSchema, self.filename_dyad)

    def remove_labels_client(self):
        """Remove all annotation labels for the client from the database"""
        return self._remove_labels(ClientAnnotationSchema)

    def remove_labels_therapist(self):
        """Remove all annotation labels for the therapist from the database"""
        return self._remove_labels(TherapistAnnotationSchema)

    def remove_labels_dyad(self):
        """Remove all annotation labels for the dyad from the database"""
        return self._remove_labels(DyadAnnotationSchema)


class AnnotationSchemaScaleManager:
    def __init__(self) -> None:
        """Initialize the manager specifying the JSON files containing the annotation schema scales"""
        self.filename_client = os.path.join(
            current_app.config["ANNOTATION_SCHEMA_SCALES_PATH"], "client.json"
        )
        self.filename_therapist = os.path.join(
            current_app.config["ANNOTATION_SCHEMA_SCALES_PATH"], "therapist.json"
        )
        self.filename_dyad = os.path.join(
            current_app.config["ANNOTATION_SCHEMA_SCALES_PATH"], "dyad.json"
        )

    def _read_json(self, filename: str):
        """Read the JSON file"""
        with open(filename, "r") as f:
            data = json.load(f)
        return data

    def _add_scales(
        self,
        annotation_schema_scale_model: Union[
            ClientAnnotationSchemaScale,
            TherapistAnnotationSchemaScale,
            DyadAnnotationSchemaScale,
        ],
        annotation_schema_model: Union[
            ClientAnnotationSchema,
            TherapistAnnotationSchema,
            DyadAnnotationSchema,
        ],
        filename: str,
    ):
        """
        Add annotation schema scales to the database.

        Parameters
        ----------
        annotation_schema_scale_model : ClientAnnotationSchemaScale or TherapistAnnotationSchemaScale or DyadAnnotationSchemaScale
            The annotation schema scale model class for the client, therapist or dyad
        annotation_schema_model : ClientAnnotationSchema or TherapistAnnotationSchema or DyadAnnotationSchema
            The annotation schema model class for the client, therapist or dyad
        filename : str
            The path to the JSON file containing the annotation schema scales
        """
        scales = self._read_json(filename)
        keys = list(scales.keys())

        try:
            for key in keys:
                label = annotation_schema_model.query.filter_by(
                    label=key.strip().capitalize()
                ).first()
                if label is not None:
                    for scale_title, scale_levels in scales[key].items():
                        for scale_level in scale_levels:
                            scale = annotation_schema_scale_model(
                                scale_title=scale_title.strip().capitalize(),
                                scale_level=scale_level.strip().capitalize(),
                                label=label,
                            )
                            db.session.add(scale)
                else:
                    warnings.warn(
                        f"Annotation label {key.strip().capitalize()} not found in {annotation_schema_model.__tablename__} table"
                    )
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            raise e

        return None

    def _remove_scales(
        self,
        annotation_schema_scale_model: Union[
            ClientAnnotationSchemaScale,
            TherapistAnnotationSchemaScale,
            DyadAnnotationSchemaScale,
        ],
    ):
        """
        Remove all annotation schema scales for the client, therapist or dyad from the database.

        Parameters
        ----------
        annotation_schema_scale_model : ClientAnnotationSchemaScale or TherapistAnnotationSchemaScale or DyadAnnotationSchemaScale
            The annotation schema scale model class for the client, therapist or dyad
        """
        try:
            annotation_schema_scale_model.query.delete()
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            raise e

        return None

    def add_scales_client(self):
        """Add annotation schema scales for the client to the database"""
        return self._add_scales(
            ClientAnnotationSchemaScale, ClientAnnotationSchema, self.filename_client
        )

    def add_scales_therapist(self):
        """Add annotation schema scales for the therapist to the database"""
        return self._add_scales(
            TherapistAnnotationSchemaScale,
            TherapistAnnotationSchema,
            self.filename_therapist,
        )

    def add_scales_dyad(self):
        """Add annotation schema scales for the dyad to the database"""
        return self._add_scales(
            DyadAnnotationSchemaScale, DyadAnnotationSchema, self.filename_dyad
        )

    def remove_scales_client(self):
        """Remove all annotation schema scales for the client from the database"""
        return self._remove_scales(ClientAnnotationSchemaScale)

    def remove_scales_therapist(self):
        """Remove all annotation schema scales for the therapist from the database"""
        return self._remove_scales(TherapistAnnotationSchemaScale)

    def remove_scales_dyad(self):
        """Remove all annotation schema scales for the dyad from the database"""
        return self._remove_scales(DyadAnnotationSchemaScale)
