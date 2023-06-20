# Desc: Upload forms for the app
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField, SelectField
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
    submit = SubmitField("Upload dataset")
    # The annotator field is a SelectField, which is a drop-down menu.
    # The coerce=int argument ensures that the value of the field is an integer.
    annotator = SelectField("Annotator", coerce=int)  # who is annotating the dataset

    def validate_name(self, name):
        """
        Validate the dataset name.
        Check that the current user does not already have a dataset with the
        same name.
        This is a custom validator, and for it to work, the function name must be
        in the format validate_<field_name>.
        """
        dataset_name = Dataset.query.filter_by(
            name=name.data,
            id_user=current_user.id,
        ).first()
        if dataset_name is not None:
            raise ValidationError(
                "Dataset name already exists. Please choose another name."
            )
