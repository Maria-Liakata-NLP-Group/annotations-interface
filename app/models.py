from app import db, login
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
from app.utils import (
    SMAnnotationType,
    DatasetType,
    Permission,
    SubLabelsA,
    SubLabelsB,
    SubLabelsC,
    SubLabelsD,
    SubLabelsE,
    LabelScale,
    Speaker,
)


@login.user_loader
def load_user(id):
    """Load user from database. Used by flask_login."""
    return User.query.get(int(id))


dataset_annotator = db.Table(
    "dataset_annotator",
    db.Column("id_dataset", db.Integer, db.ForeignKey("dataset.id")),
    db.Column("id_annotator", db.Integer, db.ForeignKey("user.id")),
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
    annotations_dialog_turn = db.relationship(
        "PSDialogTurnAnnotation", backref="author", lazy="dynamic"
    )  # one-to-many relationship with PSDialogTurnAnnotation class
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
    dialog_turns_annotations = db.relationship(
        "PSDialogTurnAnnotation", backref="dataset", lazy="dynamic"
    )  # one-to-many relationship with PSDialogTurnAnnotation class

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
    annotations = db.relationship(
        "PSDialogTurnAnnotation", backref="dialog_turn", lazy="dynamic"
    )  # one-to-many relationship with PSDialogTurnAnnotation class


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


class PSDialogTurnAnnotation(db.Model):
    """
    Psychotherapy Dialog Turn Annotation class for database.
    This captures annotations of psychotherapy sessions at the 'segment' level.
    """

    __tablename__ = "ps_dialog_turn_annotation"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.DateTime, index=True, default=datetime.utcnow
    )  # when annotation was created
    label_a = db.Column(db.Enum(SubLabelsA), nullable=True)
    label_b = db.Column(db.Enum(SubLabelsB), nullable=True)
    label_c = db.Column(db.Enum(SubLabelsC), nullable=True)
    label_d = db.Column(db.Enum(SubLabelsD), nullable=True)
    label_e = db.Column(db.Enum(SubLabelsE), nullable=True)
    strength_a = db.Column(db.Enum(LabelScale), nullable=True)
    strength_b = db.Column(db.Enum(LabelScale), nullable=True)
    strength_c = db.Column(db.Enum(LabelScale), nullable=True)
    strength_d = db.Column(db.Enum(LabelScale), nullable=True)
    strength_e = db.Column(db.Enum(LabelScale), nullable=True)
    comment_a = db.Column(db.Text, nullable=True)
    comment_b = db.Column(db.Text, nullable=True)
    comment_c = db.Column(db.Text, nullable=True)
    comment_d = db.Column(db.Text, nullable=True)
    comment_e = db.Column(db.Text, nullable=True)
    speaker = db.Column(db.Enum(Speaker), nullable=True)
    id_user = db.Column(
        db.Integer, db.ForeignKey("user.id")
    )  # id of user (annotator) who created this annotation
    id_ps_dialog_turn = db.Column(
        db.Integer, db.ForeignKey("ps_dialog_turn.id")
    )  # id of dialog turn associated with this annotation
    id_dataset = db.Column(
        db.Integer, db.ForeignKey("dataset.id")
    )  # id of dataset associated with this annotation
