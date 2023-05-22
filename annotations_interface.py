from app import app, db
from app.models import User, SMAnnotation, SMPost, SMReply


# Create shell context for flask shell
@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "SMAnnotation": SMAnnotation,
        "SMPost": SMPost,
        "SMReply": SMReply,
    }
