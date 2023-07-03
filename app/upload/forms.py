# Desc: Upload forms for the app
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    TextAreaField,
    FileField,
    SelectMultipleField,
)
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import Dataset
from flask_login import current_user


class UploadForm(FlaskForm):
    """Dataset upload form for the app"""

    name = StringField(
        "Dataset name", validators=[DataRequired(), Length(min=4, max=50)]
    )
    description = TextAreaField(
        "Please provide a short description",
        validators=[DataRequired(), Length(min=5, max=200)],
    )
    file = FileField("File", validators=[DataRequired()])
    # The annotator field is a SelectMultipleField, which allows the user to select
    # multiple annotators from a list of users.
    # The coerce=int argument ensures that the value of the field is an integer.
    annotators = SelectMultipleField(
        "Annotators", coerce=int, validators=[DataRequired()]
    )  # who will be annotating the dataset
    submit = SubmitField("Upload dataset")

    def validate_name(self, name):
        """
        Ensure that the dataset name is unique,
        and does not already exist in the database.
        This is a custom validator, and for it to work, it must
        be named "validate_<field_name>".
        """
        dataset = Dataset.query.filter_by(name=name.data).first()
        if dataset:
            raise ValidationError(
                "Dataset name already exists. Please choose another name."
            )
