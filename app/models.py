from app import db


class User(db.Model):
    """User class for database"""
    id = db.Column(db.Integer, primary_key=True)  # each user will have unique id
    username = db.Column(db.String(64), index=True, unique=True)  # index=True - for faster search
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))  # hash of password

    def __repr__(self):
        """How to print objects of this class"""
        return '<User {}>'.format(self.username)
