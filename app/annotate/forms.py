"""
Annotation forms for the app
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, TextAreaField
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    ValidationError,
    InputRequired,
)

from app.utils import (
    LabelNames,
    LabelStrength,
    SubLabelsAClient,
    SubLabelsATherapist,
    SubLabelsBClient,
    SubLabelsBTherapist,
    SubLabelsCClient,
    SubLabelsCTherapist,
    SubLabelsDClient,
    SubLabelsDTherapist,
    SubLabelsEClient,
    SubLabelsETherapist,
    LabelStrengthAClient,
    LabelStrengthATherapist,
    LabelStrengthBClient,
    LabelStrengthBTherapist,
    LabelStrengthCClient,
    LabelStrengthCTherapist,
    LabelStrengthDClient,
    LabelStrengthDTherapist,
    LabelStrengthEClient,
    LabelStrengthETherapist,
)


class RequiredIf(InputRequired):
    """Validator which makes a form field required if another field is set to a certain value."""

    field_flags = ("requiredif",)

    def __init__(self, other_field_name, value, message=None, *args, **kwargs):
        self.other_field_name = other_field_name
        self.value = value
        self.message = message

    def __call__(self, form, field):
        other_field = form[self.other_field_name]
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if (other_field.data).lower() == self.value.lower():
            super(RequiredIf, self).__call__(form, field)
        else:
            Optional().__call__(form, field)


def create_select_field(label, choices, name):
    """Create a select field with the given label, choices and name"""

    return SelectField(
        label=label,
        choices=[(choice.name, choice.value) for choice in choices],
        validators=[DataRequired()],
        name=name,
    )


def create_text_area_field(label, name, required_if, max_length=200):
    """
    Create a text area field with the given label, name and max length.
    The field is required if the field with the given name is set to the given value.
    """

    value = "other"
    message = "If you select Other, please provide a comment."
    return TextAreaField(
        label,
        validators=[RequiredIf(required_if, value, message), Length(max=max_length)],
        name=name,
    )


class PSAnnotationFormClient(FlaskForm):
    """Segment level annotation form of psychotherapy datasets for the client"""

    label_a_client = create_select_field(
        label=LabelNames.label_a_client.value,
        choices=SubLabelsAClient,
        name="label_a_client",
    )
    label_b_client = create_select_field(
        label=LabelNames.label_b_client.value,
        choices=SubLabelsBClient,
        name="label_b_client",
    )
    label_c_client = create_select_field(
        label=LabelNames.label_c_client.value,
        choices=SubLabelsCClient,
        name="label_c_client",
    )
    label_d_client = create_select_field(
        label=LabelNames.label_d_client.value,
        choices=SubLabelsDClient,
        name="label_d_client",
    )
    label_e_client = create_select_field(
        label=LabelNames.label_e_client.value,
        choices=SubLabelsEClient,
        name="label_e_client",
    )
    strength_a_client = create_select_field(
        label="Strength", choices=LabelStrength, name="strength_a_client"
    )
    strength_b = create_select_field(
        label="Strength", choices=LabelStrength, name="strength_b_client"
    )
    strength_c = create_select_field(
        label="Strength", choices=LabelStrength, name="strength_c_client"
    )
    strength_d = create_select_field(
        label="Strength", choices=LabelStrength, name="strength_d_client"
    )
    strength_e = create_select_field(
        label="Strength", choices=LabelStrength, name="strength_e_client"
    )
    comment_a = create_text_area_field(
        label="Comment", name="comment_a_client", required_if="label_a_client"
    )
    comment_b = create_text_area_field(
        label="Comment", name="comment_b_client", required_if="label_b_client"
    )
    comment_c = create_text_area_field(
        label="Comment", name="comment_c_client", required_if="label_c_client"
    )
    comment_d = create_text_area_field(
        label="Comment", name="comment_d_client", required_if="label_d_client"
    )
    comment_e = create_text_area_field(
        label="Comment", name="comment_e_client", required_if="label_e_client"
    )
    submit = SubmitField("Submit")


class PSAnnotationFormTherapist(FlaskForm):
    """Segment level annotation form of psychotherapy datasets for the therapist"""

    label_a_therapist = create_select_field(
        label=LabelNames.label_a_therapist.value,
        choices=SubLabelsATherapist,
        name="label_a_therapist",
    )
    label_b_therapist = create_select_field(
        label=LabelNames.label_b_therapist.value,
        choices=SubLabelsBTherapist,
        name="label_b_therapist",
    )
    label_c_therapist = create_select_field(
        label=LabelNames.label_c_therapist.value,
        choices=SubLabelsCTherapist,
        name="label_c_therapist",
    )
    label_d_therapist = create_select_field(
        label=LabelNames.label_d_therapist.value,
        choices=SubLabelsDTherapist,
        name="label_d_therapist",
    )
    label_e_therapist = create_select_field(
        label=LabelNames.label_e_therapist.value,
        choices=SubLabelsETherapist,
        name="label_e_therapist",
    )
    strength_a_therapist = create_select_field(
        label="Strength", choices=LabelStrength, name="strength_a_therapist"
    )
    strength_b = create_select_field(
        label="Strength", choices=LabelStrength, name="strength_b_therapist"
    )
    strength_c = create_select_field(
        label="Strength", choices=LabelStrength, name="strength_c_therapist"
    )
    strength_d = create_select_field(
        label="Strength", choices=LabelStrength, name="strength_d_therapist"
    )
    strength_e = create_select_field(
        label="Strength", choices=LabelStrength, name="strength_e_therapist"
    )
    comment_a = create_text_area_field(
        label="Comment", name="comment_a_therapist", required_if="label_a_therapist"
    )
    comment_b = create_text_area_field(
        label="Comment", name="comment_b_therapist", required_if="label_b_therapist"
    )
    comment_c = create_text_area_field(
        label="Comment", name="comment_c_therapist", required_if="label_c_therapist"
    )
    comment_d = create_text_area_field(
        label="Comment", name="comment_d_therapist", required_if="label_d_therapist"
    )
    comment_e = create_text_area_field(
        label="Comment", name="comment_e_therapist", required_if="label_e_therapist"
    )
    submit = SubmitField("Submit")
