from app import create_app, db
from app.models import (
    User,
    SMAnnotation,
    SMPost,
    SMReply,
    Dataset,
    Role,
    Permission,
    Psychotherapy,
)

app = create_app()


# Create shell context for flask shell
@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "SMAnnotation": SMAnnotation,
        "SMPost": SMPost,
        "SMReply": SMReply,
        "Dataset": Dataset,
        "Role": Role,
        "Permission": Permission,
        "Psychotherapy": Psychotherapy,
    }


@app.cli.command()
def clear_db():
    """Clear database and insert roles"""
    db.drop_all()
    db.create_all()
    Role.insert_roles()
