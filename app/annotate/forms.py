"""
Annotation forms for the app
"""
from flask_wtf import FlaskForm
from wtforms import RadioField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from app.utils import (
    LabelNames,
    LabelStrength,
    SubLabelsA,
    SubLabelsB,
    SubLabelsC,
    SubLabelsD,
    SubLabelsE,
)


def create_label_field(label_name, label_choices):
    """Create a label field for the psychotherapy annotation form"""

    return SelectField(
        label_name,
        choices=[(label.name, label.value) for label in label_choices],
        validators=[DataRequired()],
    )


def create_label_strength_field(field_name="Strength"):
    """Create a label strength field for the psychotherapy annotation form"""

    return RadioField(
        field_name,
        choices=[(strength.name, strength.value) for strength in LabelStrength],
        default=LabelStrength.medium.name,
        validators=[DataRequired()],
    )


def create_comment_field(field_name="Comment", max_length=200):
    """Create a comment field for the psychotherapy annotation form"""

    return TextAreaField(
        field_name,
        validators=[DataRequired(), Length(max=max_length)],
    )


class PSAnnotationForm(FlaskForm):
    """Annotation form for psychotherapy datasets"""

    label_a = create_label_field(LabelNames.label_a.value, SubLabelsA)
    label_b = create_label_field(LabelNames.label_b.value, SubLabelsB)
    label_c = create_label_field(LabelNames.label_c.value, SubLabelsC)
    label_d = create_label_field(LabelNames.label_d.value, SubLabelsD)
    label_e = create_label_field(LabelNames.label_e.value, SubLabelsE)
    strength_a = create_label_strength_field()
    strength_b = create_label_strength_field()
    strength_c = create_label_strength_field()
    strength_d = create_label_strength_field()
    strength_e = create_label_strength_field()
    comment_a = create_comment_field()
    comment_b = create_comment_field()
    comment_c = create_comment_field()
    comment_d = create_comment_field()
    comment_e = create_comment_field()
    submit = SubmitField("Submit")
