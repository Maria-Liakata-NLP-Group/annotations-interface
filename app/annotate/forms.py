"""
Annotation forms for the app
"""
from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
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
    Speaker,
)


def create_label_field(label, choices, name):
    """
    Create a select field for the labels in the psychotherapy annotation form

    Args:
        label: Label name (A, B, etc.)
        choices: Enum choices (sublabels) for the label
        name: The HTML name of the field

    Returns:
        A select field for the label with DataRequired validator
    """

    return SelectField(
        label=label,
        choices=[(choice.name, choice.value) for choice in choices],
        validators=[DataRequired()],
        name=name,
    )


def create_label_strength_field(label, choices, name):
    """
    Create a radio field for the label strength in the psychotherapy annotation form

    Args:
        label: Label for this radio field
        choices: Enum choices for this radio field
        name: The HTML name of the field

    Returns:
        A radio field for the label strength with DataRequired validator
    """

    return RadioField(
        label=label,
        choices=[(choice.name, choice.value) for choice in choices],
        validators=[DataRequired()],
        name=name,
    )


def create_comment_field(label, name, max_length=200):
    """
    Create a text area field for the comment in the psychotherapy annotation form

    Args:
        label: Label for this comment field
        name: The HTML name of the field
        max_length: Maximum length of the comment

    Returns:
        A text area field for the comment with DataRequired and Length validators
    """

    return TextAreaField(
        label,
        validators=[DataRequired(), Length(max=max_length)],
        name=name,
    )


class PSAnnotationFormClient(FlaskForm):
    """Segment level annotation form of psychotherapy datasets for the client"""

    label_a = create_label_field(
        label=LabelNames.label_a.value, choices=SubLabelsA, name="label_a_client"
    )
    label_b = create_label_field(
        label=LabelNames.label_b.value, choices=SubLabelsB, name="label_b_client"
    )
    label_c = create_label_field(
        label=LabelNames.label_c.value, choices=SubLabelsC, name="label_c_client"
    )
    label_d = create_label_field(
        label=LabelNames.label_d.value, choices=SubLabelsD, name="label_d_client"
    )
    label_e = create_label_field(
        label=LabelNames.label_e.value, choices=SubLabelsE, name="label_e_client"
    )
    strength_a = create_label_strength_field(
        label="Strength", choices=LabelStrength, name="strength_a_client"
    )
    strength_b = create_label_strength_field(
        label="Strength", choices=LabelStrength, name="strength_b_client"
    )
    strength_c = create_label_strength_field(
        label="Strength", choices=LabelStrength, name="strength_c_client"
    )
    strength_d = create_label_strength_field(
        label="Strength", choices=LabelStrength, name="strength_d_client"
    )
    strength_e = create_label_strength_field(
        label="Strength", choices=LabelStrength, name="strength_e_client"
    )
    comment_a = create_comment_field(label="Comment", name="comment_a_client")
    comment_b = create_comment_field(label="Comment", name="comment_b_client")
    comment_c = create_comment_field(label="Comment", name="comment_c_client")
    comment_d = create_comment_field(label="Comment", name="comment_d_client")
    comment_e = create_comment_field(label="Comment", name="comment_e_client")
    submit = SubmitField("Submit")


class PSAnnotationFormTherapist(FlaskForm):
    """Segment level annotation form of psychotherapy datasets for the therapist"""

    label_a = create_label_field(
        label=LabelNames.label_a.value, choices=SubLabelsA, name="label_a_therapist"
    )
    label_b = create_label_field(
        label=LabelNames.label_b.value, choices=SubLabelsB, name="label_b_therapist"
    )
    label_c = create_label_field(
        label=LabelNames.label_c.value, choices=SubLabelsC, name="label_c_therapist"
    )
    label_d = create_label_field(
        label=LabelNames.label_d.value, choices=SubLabelsD, name="label_d_therapist"
    )
    label_e = create_label_field(
        label=LabelNames.label_e.value, choices=SubLabelsE, name="label_e_therapist"
    )
    strength_a = create_label_strength_field(
        label="Strength", choices=LabelStrength, name="strength_a_therapist"
    )
    strength_b = create_label_strength_field(
        label="Strength", choices=LabelStrength, name="strength_b_therapist"
    )
    strength_c = create_label_strength_field(
        label="Strength", choices=LabelStrength, name="strength_c_therapist"
    )
    strength_d = create_label_strength_field(
        label="Strength", choices=LabelStrength, name="strength_d_therapist"
    )
    strength_e = create_label_strength_field(
        label="Strength", choices=LabelStrength, name="strength_e_therapist"
    )
    comment_a = create_comment_field(label="Comment", name="comment_a_therapist")
    comment_b = create_comment_field(label="Comment", name="comment_b_therapist")
    comment_c = create_comment_field(label="Comment", name="comment_c_therapist")
    comment_d = create_comment_field(label="Comment", name="comment_d_therapist")
    comment_e = create_comment_field(label="Comment", name="comment_e_therapist")
    submit = SubmitField("Submit")
