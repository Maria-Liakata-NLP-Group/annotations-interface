from app import db, login
from datetime import datetime
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class AnnotationType(Enum):
    """Enum for annotation types"""

    escalation = "Escalation"
    switch = "Switch"


@login.user_loader
def load_user(id):
    """Load user from database. Used by flask_login."""
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    """User class for database"""

    id = db.Column(db.Integer, primary_key=True)  # each user will have unique id
    username = db.Column(
        db.String(64), index=True, unique=True
    )  # index=True - for faster search
    email = db.Column(db.String(120), index=True, unique=False)
    password_hash = db.Column(db.String(128))  # hash of password
    annotations_sm = db.relationship(
        "SMAnnotation", backref="author", lazy="dynamic"
    )  # one-to-many relationship with SMAnnotation class

    def __repr__(self):
        """How to print objects of this class"""
        return "<User {}>".format(self.username)

    def set_password(self, password):
        """Set password for user"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password is correct"""
        return check_password_hash(self.password_hash, password)


class SMAnnotation(db.Model):
    """Social Media Annotation class for database"""

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(AnnotationType), nullable=True)  # type of annotation
    body = db.Column(db.Text)  # annotation body
    timestamp = db.Column(
        db.DateTime, index=True, default=datetime.utcnow
    )  # when annotation was created
    id_user = db.Column(
        db.Integer, db.ForeignKey("user.id")
    )  # id of user who created this annotation
    posts = db.relationship(
        "SMPost", backref="annotation", lazy="dynamic"
    )  # one-to-many relationship with SMPost class

    def __repr__(self):
        """How to print objects of this class"""
        return "<Social Media Annotation {}>".format(self.body)


class SMPost(db.Model):
    """Social Media Post class for database"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), index=True, unique=False)
    timeline_id = db.Column(db.String(64), index=True, unique=False)
    post_id = db.Column(db.Integer, index=True, unique=True)
    mood = db.Column(db.String(64))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    ldate = db.Column(db.DateTime, default=datetime.utcnow)
    question = db.Column(db.Text)
    id_sm_annotation = db.Column(db.Integer, db.ForeignKey("sm_annotation.id"))
    replies = db.relationship(
        "SMReply", backref="post", lazy="dynamic"
    )  # one-to-many relationship with SMReply class

    def __repr__(self):
        """How to print objects of this class"""
        return "<Social Media Post {}>".format(self.question)


class SMReply(db.Model):
    """Social Media Reply class for database"""

    id = db.Column(db.Integer, primary_key=True)
    reply_id = db.Column(db.Integer, index=True, unique=True)
    user_id = db.Column(db.String(64), index=True, unique=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    ldate = db.Column(db.DateTime, default=datetime.utcnow)
    comment = db.Column(db.Text)
    id_sm_post = db.Column(db.Integer, db.ForeignKey("sm_post.id"))

    def __repr__(self):
        """How to print objects of this class"""
        return "<Social Media Reply {}>".format(self.comment)
