from app import db, login
from datetime import datetime, date
import json
from typing import Union
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app, abort
import warnings
import os
from sqlalchemy.ext.associationproxy import association_proxy
from app.utils import (
    SMAnnotationType,
    DatasetType,
    Permission,
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


class ClientAnnotationLabelAssociation(db.Model):
    """Associtation object for many-to-many relationship between PSAnnotationClient and ClientAnnotationLabel"""

    __tablename__ = "annotationclient_annotationlabel"
    id = db.Column(db.Integer, primary_key=True)
    id_ps_annotation_client = db.Column(
        db.Integer,
        db.ForeignKey("ps_annotation_client.id"),
        nullable=False,
    )
    id_client_annotation_label = db.Column(
        db.Integer,
        db.ForeignKey("client_annotation_label.id"),
        nullable=False,
    )
    is_additional = db.Column(db.Boolean, default=False)  # is this an additional label?
    label = db.relationship(
        "ClientAnnotationLabel",
        back_populates="annotations",
    )
    annotation = db.relationship(
        "PSAnnotationClient",
        back_populates="annotation_label_associations",
    )

    def __init__(self, label=None, annotation=None, is_additional=False):
        self.label = label
        self.annotation = annotation
        self.is_additional = is_additional


class TherapistAnnotationLabelAssociation(db.Model):
    """Associtation object for many-to-many relationship between PSAnnotationTherapist and TherapistAnnotationLabel"""

    __tablename__ = "annotationtherapist_annotationlabel"
    id = db.Column(db.Integer, primary_key=True)
    id_ps_annotation_therapist = db.Column(
        db.Integer,
        db.ForeignKey("ps_annotation_therapist.id"),
        nullable=False,
    )
    id_therapist_annotation_label = db.Column(
        db.Integer,
        db.ForeignKey("therapist_annotation_label.id"),
        nullable=False,
    )
    is_additional = db.Column(db.Boolean, default=False)  # is this an additional label?
    label = db.relationship(
        "TherapistAnnotationLabel",
        back_populates="annotations",
    )
    annotation = db.relationship(
        "PSAnnotationTherapist",
        back_populates="annotation_label_associations",
    )

    def __init__(self, label=None, annotation=None, is_additional=False):
        self.label = label
        self.annotation = annotation
        self.is_additional = is_additional


class DyadAnnotationLabelAssociation(db.Model):
    """Associtation object for many-to-many relationship between PSAnnotationDyad and DyadAnnotationLabel"""

    __tablename__ = "annotationdyad_annotationlabel"
    id = db.Column(db.Integer, primary_key=True)
    id_ps_annotation_dyad = db.Column(
        db.Integer,
        db.ForeignKey("ps_annotation_dyad.id"),
        nullable=False,
    )
    id_dyad_annotation_label = db.Column(
        db.Integer,
        db.ForeignKey("dyad_annotation_label.id"),
        nullable=False,
    )
    is_additional = db.Column(db.Boolean, default=False)  # is this an additional label?
    label = db.relationship(
        "DyadAnnotationLabel",
        back_populates="annotations",
    )
    annotation = db.relationship(
        "PSAnnotationDyad",
        back_populates="annotation_label_associations",
    )

    def __init__(self, label=None, annotation=None, is_additional=False):
        self.label = label
        self.annotation = annotation
        self.is_additional = is_additional


class ClientAnnotationScaleAssociation(db.Model):
    """Association object for many-to-many relationship between PSAnnotationClient and ClientAnnotationScale"""

    __tablename__ = "annotationclient_annotationscale"
    id = db.Column(db.Integer, primary_key=True)
    id_ps_annotation_client = db.Column(
        db.Integer,
        db.ForeignKey("ps_annotation_client.id"),
        nullable=False,
    )
    id_client_annotation_scale = db.Column(
        db.Integer,
        db.ForeignKey("client_annotation_scale.id"),
        nullable=False,
    )
    is_additional = db.Column(db.Boolean, default=False)  # is this an additional scale?
    scale = db.relationship(
        "ClientAnnotationScale",
        back_populates="annotations",
    )
    annotation = db.relationship(
        "PSAnnotationClient",
        back_populates="annotation_scale_associations",
    )

    def __init__(self, scale=None, annotation=None, is_additional=False):
        self.scale = scale
        self.annotation = annotation
        self.is_additional = is_additional


class TherapistAnnotationScaleAssociation(db.Model):
    """Association object for many-to-many relationship between PSAnnotationTherapist and TherapistAnnotationScale"""

    __tablename__ = "annotationtherapist_annotationscale"
    id = db.Column(db.Integer, primary_key=True)
    id_ps_annotation_therapist = db.Column(
        db.Integer,
        db.ForeignKey("ps_annotation_therapist.id"),
        nullable=False,
    )
    id_therapist_annotation_scale = db.Column(
        db.Integer,
        db.ForeignKey("therapist_annotation_scale.id"),
        nullable=False,
    )
    is_additional = db.Column(db.Boolean, default=False)  # is this an additional scale?
    scale = db.relationship(
        "TherapistAnnotationScale",
        back_populates="annotations",
    )
    annotation = db.relationship(
        "PSAnnotationTherapist",
        back_populates="annotation_scale_associations",
    )

    def __init__(self, scale=None, annotation=None, is_additional=False):
        self.scale = scale
        self.annotation = annotation
        self.is_additional = is_additional


class DyadAnnotationScaleAssociation(db.Model):
    """Association object for many-to-many relationship between PSAnnotationDyad and DyadAnnotationScale"""

    __tablename__ = "annotationdyad_annotationscale"
    id = db.Column(db.Integer, primary_key=True)
    id_ps_annotation_dyad = db.Column(
        db.Integer,
        db.ForeignKey("ps_annotation_dyad.id"),
        nullable=False,
    )
    id_dyad_annotation_scale = db.Column(
        db.Integer,
        db.ForeignKey("dyad_annotation_scale.id"),
        nullable=False,
    )
    is_additional = db.Column(db.Boolean, default=False)  # is this an additional scale?
    scale = db.relationship(
        "DyadAnnotationScale",
        back_populates="annotations",
    )
    annotation = db.relationship(
        "PSAnnotationDyad",
        back_populates="annotation_scale_associations",
    )

    def __init__(self, scale=None, annotation=None, is_additional=False):
        self.scale = scale
        self.annotation = annotation
        self.is_additional = is_additional


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
    comment_summary = db.Column(db.Text, nullable=True)
    id_user = db.Column(
        db.Integer, db.ForeignKey("user.id")
    )  # id of user (annotator) who created this annotation
    id_dataset = db.Column(
        db.Integer, db.ForeignKey("dataset.id")
    )  # id of dataset associated with this annotation
    dialog_turns = db.relationship(
        "PSDialogTurn",
        secondary=annotationclient_dialogturn,
        backref=db.backref("annotations_client", lazy="dynamic"),
        lazy="dynamic",
    )  # many-to-many relationship with PSDialogTurn class
    evidence = db.relationship(
        "EvidenceClient", backref="annotation", lazy="dynamic"
    )  # one-to-many relationship with EvidenceClient class
    annotation_label_associations = db.relationship(
        "ClientAnnotationLabelAssociation",
        back_populates="annotation",
        lazy="dynamic",
    )  # many-to-many relationship with ClientAnnotationLabel class
    annotation_scale_associations = db.relationship(
        "ClientAnnotationScaleAssociation",
        back_populates="annotation",
        lazy="dynamic",
    )  # many-to-many relationship with ClientAnnotationScale class
    annotation_labels = association_proxy(
        "annotation_label_associations", "label"
    )  # association proxy of "annotation_label_associations" to "label" attribute of ClientAnnotationLabelAssociation class
    annotation_scales = association_proxy(
        "annotation_scale_associations", "scale"
    )  # association proxy of "annotation_scale_associations" to "scale" attribute of ClientAnnotationScaleAssociation class
    annotation_comments = db.relationship(
        "ClientAnnotationComment",
        backref="annotation",
        lazy="dynamic",
    )  # one-to-many relationship with ClientAnnotationComment class


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
    comment_summary = db.Column(db.Text, nullable=True)
    id_user = db.Column(
        db.Integer, db.ForeignKey("user.id")
    )  # id of user (annotator) who created this annotation
    id_dataset = db.Column(
        db.Integer, db.ForeignKey("dataset.id")
    )  # id of dataset associated with this annotation
    dialog_turns = db.relationship(
        "PSDialogTurn",
        secondary=annotationtherapist_dialogturn,
        backref=db.backref("annotations_therapist", lazy="dynamic"),
        lazy="dynamic",
    )  # many-to-many relationship with PSDialogTurn class
    evidence = db.relationship(
        "EvidenceTherapist", backref="annotation", lazy="dynamic"
    )  # one-to-many relationship with EvidenceTherapist class
    annotation_label_associations = db.relationship(
        "TherapistAnnotationLabelAssociation",
        back_populates="annotation",
        lazy="dynamic",
    )  # many-to-many relationship with TherapistAnnotationLabel class
    annotation_scale_associations = db.relationship(
        "TherapistAnnotationScaleAssociation",
        back_populates="annotation",
        lazy="dynamic",
    )  # many-to-many relationship with TherapistAnnotationScale class
    annotation_labels = association_proxy(
        "annotation_label_associations", "label"
    )  # association proxy of "annotation_label_associations" to "label" attribute of TherapistAnnotationLabelAssociation class
    annotation_scales = association_proxy(
        "annotation_scale_associations", "scale"
    )  # association proxy of "annotation_scale_associations" to "scale" attribute of TherapistAnnotationScaleAssociation class
    annotation_comments = db.relationship(
        "TherapistAnnotationComment",
        backref="annotation",
        lazy="dynamic",
    )  # one-to-many relationship with TherapistAnnotationComment class


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
    comment_summary = db.Column(db.Text, nullable=True)
    id_user = db.Column(
        db.Integer, db.ForeignKey("user.id")
    )  # id of user (annotator) who created this annotation
    id_dataset = db.Column(
        db.Integer, db.ForeignKey("dataset.id")
    )  # id of dataset associated with this annotation
    dialog_turns = db.relationship(
        "PSDialogTurn",
        secondary=annotationsdyad_dialogturn,
        backref=db.backref("annotations_dyad", lazy="dynamic"),
        lazy="dynamic",
    )  # many-to-many relationship with PSDialogTurn class
    evidence = db.relationship(
        "EvidenceDyad", backref="annotation", lazy="dynamic"
    )  # one-to-many relationship with EvidenceDyad class
    annotation_label_associations = db.relationship(
        "DyadAnnotationLabelAssociation",
        back_populates="annotation",
        lazy="dynamic",
    )  # many-to-many relationship with DyadAnnotationLabel class
    annotation_scale_associations = db.relationship(
        "DyadAnnotationScaleAssociation",
        back_populates="annotation",
        lazy="dynamic",
    )  # many-to-many relationship with DyadAnnotationScale class
    annotation_labels = association_proxy(
        "annotation_label_associations", "label"
    )  # association proxy of "annotation_label_associations" to "label" attribute of DyadAnnotationLabelAssociation class
    annotation_scales = association_proxy(
        "annotation_scale_associations", "scale"
    )  # association proxy of "annotation_scale_associations" to "scale" attribute of DyadAnnotationScaleAssociation class
    annotation_comments = db.relationship(
        "DyadAnnotationComment",
        backref="annotation",
        lazy="dynamic",
    )  # one-to-many relationship with DyadAnnotationComment class


class EvidenceClient(db.Model):
    """Table to store the dialog events that are marked as evidence for a particular annotation for the client"""

    __tablename__ = "evidence_client"
    id = db.Column(db.Integer, primary_key=True)
    id_ps_dialog_event = db.Column(db.Integer, db.ForeignKey("ps_dialog_event.id"))
    id_ps_annotation_client = db.Column(
        db.Integer, db.ForeignKey("ps_annotation_client.id")
    )
    id_client_annotation_label = db.Column(
        db.Integer, db.ForeignKey("client_annotation_label.id")
    )
    is_additional = db.Column(
        db.Boolean, default=False
    )  # is this evidence for an additional label?


class EvidenceTherapist(db.Model):
    """Table to store the dialog events that are marked as evidence for a particular annotation for the therapist"""

    __tablename__ = "evidence_therapist"
    id = db.Column(db.Integer, primary_key=True)
    id_ps_dialog_event = db.Column(db.Integer, db.ForeignKey("ps_dialog_event.id"))
    id_ps_annotation_therapist = db.Column(
        db.Integer, db.ForeignKey("ps_annotation_therapist.id")
    )
    id_therapist_annotation_label = db.Column(
        db.Integer, db.ForeignKey("therapist_annotation_label.id")
    )
    is_additional = db.Column(
        db.Boolean, default=False
    )  # is this evidence for an additional label?


class EvidenceDyad(db.Model):
    """Table to store the dialog events that are marked as evidence for a particular annotation for the dyad"""

    __tablename__ = "evidence_dyad"
    id = db.Column(db.Integer, primary_key=True)
    id_ps_dialog_event = db.Column(db.Integer, db.ForeignKey("ps_dialog_event.id"))
    id_ps_annotation_dyad = db.Column(
        db.Integer, db.ForeignKey("ps_annotation_dyad.id")
    )
    id_dyad_annotation_label = db.Column(
        db.Integer, db.ForeignKey("dyad_annotation_label.id")
    )
    is_additional = db.Column(
        db.Boolean, default=False
    )  # is this evidence for an additional label?


class AnnotationLabelMixin:
    """Mixin class for annotation label classes"""

    def _find_label(self, label: Union[int, str], parent: str = None) -> object:
        """
        Given an annotation label, query the database to find the corresponding label object.

        Parameters
        ----------
        label : int or str
            The annotation label ID or name
        parent : str
            The parent label name, used when a label name is passed as the "label" parameter

        Returns
        -------
        label : object
            The label object
        """

        if isinstance(label, int):
            label = self.query.get_or_404(label)
        elif isinstance(label, str):
            label = label.strip().capitalize()
            labels = self.query.filter_by(label=label).all()
            if not labels:
                print(f"Label '{label}' does not exist")
                abort(404)
            elif parent:
                parent = parent.strip().capitalize()
                labels = [
                    label
                    for label in labels
                    if label.parent and label.parent.label == parent
                ]
                if not labels:
                    print(f"Label '{label}' with given parent does not exist")
                    abort(404)
            if len(labels) > 1:
                warnings.warn(
                    f"Multiple labels with the name '{label}' exist. "
                    f"Using the first one with ID {labels[0].id}."
                )
            label = labels[0]
        return label

    def _append_placeholder(self, choices: list) -> list:
        """Append a placeholder choice to a list of choices"""
        choices = [(0, "Select one...")] + choices
        return choices

    def get_label_children(
        self,
        label: Union[int, str],
        parent: str = None,
        append_placeholder: bool = True,
    ) -> list:
        """
        Given an annotation label, query the database to find its child labels
        so that they can be used as choices for the annotation form select fields.

        Parameters
        ----------
        label : int or str
            The annotation label ID or name
        parent : str
            The parent label name, used when a label name is passed as the "label" parameter
        append_placeholder : bool
            Whether to append a placeholder choice to the list of choices

        Returns
        -------
        choices : list
            A list of of tuples containing the child label IDs and names, to be used as choices
            for the select fields in the annotation form. If 'append_placeholder' is True, a placeholder
            choice is appended to the list of choices.
        """
        label = self._find_label(label, parent)
        children = label.children
        choices = [(label.id, label.label) for label in children]
        # sort by label id
        choices = sorted(choices, key=lambda x: x[0])
        if choices and append_placeholder:
            choices = self._append_placeholder(choices)
        return choices

    def get_label_scale_titles(
        self, label: Union[int, str], parent: str = None
    ) -> list:
        """
        Given an annotation label, query the database to find its scale titles.

        Parameters
        ----------
        label : int or str
            The annotation label ID or name
        parent : str
            The parent label name, used when a label name is passed as the "label" parameter

        Returns
        -------
        scale_titles : list
            A list of scale titles
        """
        label = self._find_label(label, parent)
        scale_titles = [scale.scale_title for scale in label.scales]
        scale_titles = sorted(list(set(scale_titles)))  # remove duplicates
        return scale_titles

    def get_label_scales(
        self,
        label: Union[int, str],
        scale_title: str,
        append_placeholder: bool = True,
    ):
        """
        Given a parent label of the annotation schema (i.e. a label with no parent), find
        its scales in the annotation schema scales so that they can be used as choices for the
        annotation form select fields.

        Parameters
        ----------
        label : int or str
            The annotation label ID or name. It must be a parent label (i.e. a label with no parent).
        scale_title : str
            The scale title.

        Returns
        -------
        choices : list
            A list of of tuples containing the scale level IDs and names, to be used as choices
            for the select fields in the annotation form. If 'append_placeholder' is True, a placeholder
            choice is appended to the list of choices.
        """

        label = self._find_label(label)
        if label.parent:
            print("Label is not a parent label")
            abort(404)
        scale_title = scale_title.strip().capitalize()
        scales = label.scales.filter_by(scale_title=scale_title).all()
        if not scales:
            warnings.warn(
                f"No scales with the title '{scale_title}' exist for the label '{label.label}'."
            )
            return []
        choices = [(scale.id, scale.scale_level) for scale in scales]
        # sort by scale id
        choices = sorted(choices, key=lambda x: x[0])
        if choices and append_placeholder:
            choices = self._append_placeholder(choices)
        return choices

    def find_parent_labels(self) -> list:
        """
        Find all parent labels of the annotation schema (i.e. labels with no parent).

        Returns
        -------
        parent_labels : list
            A list of parent label objects
        """

        parent_labels = self.query.filter_by(parent_id=None).all()
        return parent_labels

    def find_parent_label_depth(self, label: Union[int, str]) -> int:
        """
        Given a parent label of the annotation schema (i.e. a label with no parent), find
        its depth (i.e. how many levels of child labels it has) in the annotation schema tree.

        Parameters
        ----------
        label : int or str
            The annotation label ID or name. It must be a parent label (i.e. a label with no parent).

        Returns
        -------
        depth : int
            The deepest level of the label in the annotation schema tree
        """

        label = self._find_label(label)
        if label.parent:
            print("Label is not a parent label")
            abort(404)

        def find_deepest_level(label):
            """Recursively find the depth of a label in the annotation schema tree."""
            # Base case: If the label has no children, it is a leaf label.
            if not label.children.all():
                return 0

            # Initialize the maximum depth to the current depth.
            max_depth = 0

            # Recursively explore each child label.
            for child in label.children.all():
                # Calculate the depth of the child label.
                child_depth = find_deepest_level(child)
                # Update the maximum depth if the child's depth is greater.
                max_depth = max(max_depth, child_depth)

            # Add 1 to the maximum depth to account for the current label.
            return max_depth + 1

        return find_deepest_level(label)

    def find_labels_without_children(self, parent: Union[int, str]):
        """
        Given a parent label of the annotation schema (i.e. a label with no parent), find
        its child labels that have no children of their own.

        Parameters
        ----------
        parent : int or str
            The annotation label ID or name. It must be a parent label (i.e. a label with no parent).

        Returns
        -------
        labels : list
            A list of label objects that have no children
        """

        parent = self._find_label(parent)
        if parent.parent:
            print(f"Label {parent.label} is not a parent label")
            abort(404)
        labels = parent.children.filter_by(children=None).all()
        return labels


class ClientAnnotationLabel(db.Model, AnnotationLabelMixin):
    """Self-referencing table to store the client annotation labels"""

    __tablename__ = "client_annotation_label"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64), index=True, nullable=False)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("client_annotation_label.id"), default=None
    )
    children = db.relationship(
        "ClientAnnotationLabel",
        backref=db.backref("parent", remote_side=[id]),
        lazy="dynamic",
    )
    annotations = db.relationship(
        "ClientAnnotationLabelAssociation",
        back_populates="label",
        lazy="dynamic",
    )  # many-to-many relationship with PSAnnotationClient class
    scales = db.relationship(
        "ClientAnnotationScale",
        backref="label",
        lazy="dynamic",
    )  # one-to-many relationship with ClientAnnotationScale class
    comments = db.relationship(
        "ClientAnnotationComment",
        backref="label",
        lazy="dynamic",
    )  # one-to-many relationship with ClientAnnotationComment class
    # create unique constraint on label within a parent
    evidence_events = db.relationship(
        "EvidenceClient",
        backref="label",
        lazy="dynamic",
    )  # one-to-many relationship with EvidenceClient class
    __table_args__ = (db.UniqueConstraint("label", "parent_id"),)

    def __repr__(self):
        """How to print objects of this class"""
        return "<ClientAnnotationLabel {}>".format(self.label[:10])


class TherapistAnnotationLabel(db.Model, AnnotationLabelMixin):
    """Self-referencing table to store the therapist annotation labels"""

    __tablename__ = "therapist_annotation_label"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64), index=True, nullable=False)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("therapist_annotation_label.id"), default=None
    )
    children = db.relationship(
        "TherapistAnnotationLabel",
        backref=db.backref("parent", remote_side=[id]),
        lazy="dynamic",
    )
    scales = db.relationship(
        "TherapistAnnotationScale",
        backref="label",
        lazy="dynamic",
    )  # one-to-many relationship with TherapistAnnotationScale class
    comments = db.relationship(
        "TherapistAnnotationComment",
        backref="label",
        lazy="dynamic",
    )  # one-to-many relationship with TherapistAnnotationComment class
    annotations = db.relationship(
        "TherapistAnnotationLabelAssociation",
        back_populates="label",
        lazy="dynamic",
    )  # many-to-many relationship with PSAnnotationTherapist class
    evidence_events = db.relationship(
        "EvidenceTherapist",
        backref="label",
        lazy="dynamic",
    )  # one-to-many relationship with EvidenceTherapist class
    # create unique constraint on label within a parent
    __table_args__ = (db.UniqueConstraint("label", "parent_id"),)

    def __repr__(self):
        """How to print objects of this class"""
        return "<TherapistAnnotationLabel {}>".format(self.label[:10])


class DyadAnnotationLabel(db.Model, AnnotationLabelMixin):
    """Self-referencing table to store the dyad annotation schema"""

    __tablename__ = "dyad_annotation_label"
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64), index=True, nullable=False)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("dyad_annotation_label.id"), default=None
    )
    children = db.relationship(
        "DyadAnnotationLabel",
        backref=db.backref("parent", remote_side=[id]),
        lazy="dynamic",
    )
    annotations = db.relationship(
        "DyadAnnotationLabelAssociation",
        back_populates="label",
        lazy="dynamic",
    )  # many-to-many relationship with PSAnnotationDyad class
    scales = db.relationship(
        "DyadAnnotationScale",
        backref="label",
        lazy="dynamic",
    )  # one-to-many relationship with DyadAnnotationScale class
    comments = db.relationship(
        "DyadAnnotationComment",
        backref="label",
        lazy="dynamic",
    )  # one-to-many relationship with DyadAnnotationComment class
    evidence_events = db.relationship(
        "EvidenceDyad",
        backref="label",
        lazy="dynamic",
    )  # one-to-many relationship with EvidenceDyad class
    # create unique constraint on label within a parent
    __table_args__ = (db.UniqueConstraint("label", "parent_id"),)

    def __repr__(self):
        """How to print objects of this class"""
        return "<DyadAnnotationLabel {}>".format(self.label[:10])


class ClientAnnotationScale(db.Model):
    """Table to store the scales for the client annotation schema"""

    __tablename__ = "client_annotation_scale"

    id = db.Column(db.Integer, primary_key=True)
    scale_title = db.Column(db.String(64), index=True, nullable=False)
    scale_level = db.Column(db.String(64), index=True, nullable=False)
    id_client_annotation_label = db.Column(
        db.Integer, db.ForeignKey("client_annotation_label.id")
    )
    annotations = db.relationship(
        "ClientAnnotationScaleAssociation",
        back_populates="scale",
        lazy="dynamic",
    )  # many-to-many relationship with PSAnnotationClient class
    # create unique constraint on scale_title, scale_level and id_client_annotation_label
    __table_args__ = (
        db.UniqueConstraint("scale_title", "scale_level", "id_client_annotation_label"),
    )

    def __repr__(self):
        """How to print objects of this class"""
        return "<ClientAnnotationScale {}>".format(self.scale_title[:10])


class TherapistAnnotationScale(db.Model):
    """Table to store the scales for the therapist annotation schema"""

    __tablename__ = "therapist_annotation_scale"

    id = db.Column(db.Integer, primary_key=True)
    scale_title = db.Column(db.String(64), index=True, nullable=False)
    scale_level = db.Column(db.String(64), index=True, nullable=False)
    id_therapist_annotation_label = db.Column(
        db.Integer, db.ForeignKey("therapist_annotation_label.id")
    )
    annotations = db.relationship(
        "TherapistAnnotationScaleAssociation",
        back_populates="scale",
        lazy="dynamic",
    )  # many-to-many relationship with PSAnnotationTherapist class
    # create unique constraint on scale_title, scale_level and id_therapist_annotation_label
    __table_args__ = (
        db.UniqueConstraint(
            "scale_title", "scale_level", "id_therapist_annotation_label"
        ),
    )

    def __repr__(self):
        """How to print objects of this class"""
        return "<TherapistAnnotationScale {}>".format(self.scale_title[:10])


class DyadAnnotationScale(db.Model):
    """Table to store the scales for the dyad annotation schema"""

    __tablename__ = "dyad_annotation_scale"

    id = db.Column(db.Integer, primary_key=True)
    scale_title = db.Column(db.String(64), index=True, nullable=False)
    scale_level = db.Column(db.String(64), index=True, nullable=False)
    id_dyad_annotation_label = db.Column(
        db.Integer, db.ForeignKey("dyad_annotation_label.id")
    )
    annotations = db.relationship(
        "DyadAnnotationScaleAssociation",
        back_populates="scale",
        lazy="dynamic",
    )  # many-to-many relationship with PSAnnotationDyad class
    # create unique constraint on scale_title, scale_level and id_dyad_annotation_label
    __table_args__ = (
        db.UniqueConstraint("scale_title", "scale_level", "id_dyad_annotation_label"),
    )

    def __repr__(self):
        """How to print objects of this class"""
        return "<DyadAnnotationScale {}>".format(self.scale_title[:10])


class ClientAnnotationComment(db.Model):
    """Table to store the comments for the client annotation schema"""

    __tablename__ = "client_annotation_comment"

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=True)
    id_client_annotation_label = db.Column(
        db.Integer, db.ForeignKey("client_annotation_label.id")
    )
    id_ps_annotation_client = db.Column(
        db.Integer, db.ForeignKey("ps_annotation_client.id")
    )
    is_additional = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """How to print objects of this class"""
        return "<ClientAnnotationComment {}>".format(self.comment[:10])


class TherapistAnnotationComment(db.Model):
    """Table to store the comments for the therapist annotation schema"""

    __tablename__ = "therapist_annotation_comment"

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=True)
    id_therapist_annotation_label = db.Column(
        db.Integer, db.ForeignKey("therapist_annotation_label.id")
    )
    id_ps_annotation_therapist = db.Column(
        db.Integer, db.ForeignKey("ps_annotation_therapist.id")
    )
    is_additional = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """How to print objects of this class"""
        return "<TherapistAnnotationComment {}>".format(self.comment[:10])


class DyadAnnotationComment(db.Model):
    """Table to store the comments for the dyad annotation schema"""

    __tablename__ = "dyad_annotation_comment"

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=True)
    id_dyad_annotation_label = db.Column(
        db.Integer, db.ForeignKey("dyad_annotation_label.id")
    )
    id_ps_annotation_dyad = db.Column(
        db.Integer, db.ForeignKey("ps_annotation_dyad.id")
    )
    is_additional = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """How to print objects of this class"""
        return "<DyadAnnotationComment {}>".format(self.comment[:10])


class AnnotationLabelManager:
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
            ClientAnnotationLabel, TherapistAnnotationLabel, DyadAnnotationLabel
        ],
        filename: str,
    ):
        """
        Add annotation labels to the database.

        Parameters
        ----------
        annotation_schema_model : ClientAnnotationLabel or TherapistAnnotationLabel or DyadAnnotationLabel
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
            ClientAnnotationLabel, TherapistAnnotationLabel, DyadAnnotationLabel
        ],
    ):
        """
        Remove all annotation labels for the client, therapist or dyad from the database.

        Parameters
        ----------
        annotation_schema_model : ClientAnnotationLabel or TherapistAnnotationLabel or DyadAnnotationLabel
            The annotation schema model class for the client, therapist or dyad
        """
        try:
            labels = annotation_schema_model.query.all()
            for label in labels:
                db.session.delete(label)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            raise e

        return None

    def add_labels_client(self):
        """Add annotation labels for the client to the database"""
        return self._add_labels(ClientAnnotationLabel, self.filename_client)

    def add_labels_therapist(self):
        """Add annotation labels for the therapist to the database"""
        return self._add_labels(TherapistAnnotationLabel, self.filename_therapist)

    def add_labels_dyad(self):
        """Add annotation labels for the dyad to the database"""
        return self._add_labels(DyadAnnotationLabel, self.filename_dyad)

    def remove_labels_client(self):
        """Remove all annotation labels for the client from the database"""
        return self._remove_labels(ClientAnnotationLabel)

    def remove_labels_therapist(self):
        """Remove all annotation labels for the therapist from the database"""
        return self._remove_labels(TherapistAnnotationLabel)

    def remove_labels_dyad(self):
        """Remove all annotation labels for the dyad from the database"""
        return self._remove_labels(DyadAnnotationLabel)


class AnnotationScaleManager:
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
            ClientAnnotationScale,
            TherapistAnnotationScale,
            DyadAnnotationScale,
        ],
        annotation_schema_model: Union[
            ClientAnnotationLabel,
            TherapistAnnotationLabel,
            DyadAnnotationLabel,
        ],
        filename: str,
    ):
        """
        Add annotation schema scales to the database.

        Parameters
        ----------
        annotation_schema_scale_model : ClientAnnotationScale or TherapistAnnotationScale or DyadAnnotationScale
            The annotation schema scale model class for the client, therapist or dyad
        annotation_schema_model : ClientAnnotationLabel or TherapistAnnotationLabel or DyadAnnotationLabel
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
            ClientAnnotationScale,
            TherapistAnnotationScale,
            DyadAnnotationScale,
        ],
    ):
        """
        Remove all annotation schema scales for the client, therapist or dyad from the database.

        Parameters
        ----------
        annotation_schema_scale_model : ClientAnnotationScale or TherapistAnnotationScale or DyadAnnotationScale
            The annotation schema scale model class for the client, therapist or dyad
        """
        try:
            scales = annotation_schema_scale_model.query.all()
            for scale in scales:
                db.session.delete(scale)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            raise e

        return None

    def add_scales_client(self):
        """Add annotation schema scales for the client to the database"""
        return self._add_scales(
            ClientAnnotationScale, ClientAnnotationLabel, self.filename_client
        )

    def add_scales_therapist(self):
        """Add annotation schema scales for the therapist to the database"""
        return self._add_scales(
            TherapistAnnotationScale,
            TherapistAnnotationLabel,
            self.filename_therapist,
        )

    def add_scales_dyad(self):
        """Add annotation schema scales for the dyad to the database"""
        return self._add_scales(
            DyadAnnotationScale, DyadAnnotationLabel, self.filename_dyad
        )

    def remove_scales_client(self):
        """Remove all annotation schema scales for the client from the database"""
        return self._remove_scales(ClientAnnotationScale)

    def remove_scales_therapist(self):
        """Remove all annotation schema scales for the therapist from the database"""
        return self._remove_scales(TherapistAnnotationScale)

    def remove_scales_dyad(self):
        """Remove all annotation schema scales for the dyad from the database"""
        return self._remove_scales(DyadAnnotationScale)
