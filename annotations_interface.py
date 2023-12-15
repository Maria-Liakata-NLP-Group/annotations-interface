from app import create_app, db
from app.models import (
    User,
    SMAnnotation,
    SMPost,
    SMReply,
    Dataset,
    Role,
    Permission,
    PSDialogTurn,
    PSDialogEvent,
    PSAnnotationClient,
    AnnotationLabelManager,
    AnnotationScaleManager,
)
from flask_migrate import upgrade

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
        "PSDialogTurn": PSDialogTurn,
        "PSDialogEvent": PSDialogEvent,
        "PSAnnotationClient": PSAnnotationClient,
    }


@app.cli.command()
def clear_db():
    """Clear database and insert roles"""
    db.drop_all()
    db.create_all()
    Role.insert_roles()


@app.cli.command()
def create_annotation_schema():
    """Create the annotation schema for the client, therapist and dyad"""
    label_manager = AnnotationLabelManager()
    scale_manager = AnnotationScaleManager()

    # remove any existing schema first
    label_manager.remove_labels_client()
    label_manager.remove_labels_therapist()
    label_manager.remove_labels_dyad()

    scale_manager.remove_scales_client()
    scale_manager.remove_scales_therapist()
    scale_manager.remove_scales_dyad()

    # create the schema
    label_manager.add_labels_client()
    label_manager.add_labels_therapist()
    label_manager.add_labels_dyad()

    scale_manager.add_scales_client()
    scale_manager.add_scales_therapist()
    scale_manager.add_scales_dyad()


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()
    # create or update user roles
    Role.insert_roles()
    # create annotation schema
    label_manager = AnnotationLabelManager()
    scale_manager = AnnotationScaleManager()
    label_manager.add_labels_client()
    label_manager.add_labels_therapist()
    label_manager.add_labels_dyad()
    scale_manager.add_scales_client()
    scale_manager.add_scales_therapist()
    scale_manager.add_scales_dyad()
