# Desc: Upload forms for the app
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import Dataset


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

    def validate_name(self, name):
        """
        Validate the dataset name.
        This is a custom validator, and for it to work, the function name must be
        in the format validate_<field_name>.
        """
        file_name = Dataset.query.filter_by(name=name.data).first()
        if file_name is not None:
            raise ValidationError(
                "Dataset name already exists. Please choose another name."
            )
