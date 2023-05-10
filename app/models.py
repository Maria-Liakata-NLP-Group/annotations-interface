from app import db
from datetime import datetime
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash


class PostType(Enum):
    """Enum for post types"""

    escalation = "Escalation"
    switch = "Switch"


class User(db.Model):
    """User class for database"""

    id = db.Column(db.Integer, primary_key=True)  # each user will have unique id
    username = db.Column(
        db.String(64), index=True, unique=True
    )  # index=True - for faster search
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))  # hash of password
    posts = db.relationship(
        "Post", backref="author", lazy="dynamic"
    )  # one-to-many relationship with Post class

    def __repr__(self):
        """How to print objects of this class"""
        return "<User {}>".format(self.username)

    def set_password(self, password):
        """Set password for user"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password is correct"""
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    """Post class for database"""

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(PostType), nullable=True)  # type of post
    body = db.Column(db.String(140))  # post body
    timestamp = db.Column(
        db.DateTime, index=True, default=datetime.utcnow
    )  # when post was created
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id")
    )  # id of user who created this post

    def __repr__(self):
        """How to print objects of this class"""
        return "<Post {}>".format(self.body)
