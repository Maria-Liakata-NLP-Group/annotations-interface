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
from app.models import Dataset, User


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
        Check that none of the selected annotators already
        have a dataset assigned to them with the same name.
        """
        annotators = self.annotators.data
        datasets = Dataset.query.filter_by(name=name.data).all()
        for dataset in datasets:
            for annotator in annotators:
                annotator = User.query.get(annotator)
                if annotator in dataset.annotators.all():
                    raise ValidationError(
                        f"User '{annotator.username}' already has a dataset with the name '{name.data}'"
                    )
