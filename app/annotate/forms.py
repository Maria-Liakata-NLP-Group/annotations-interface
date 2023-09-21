"""
Annotation forms for the app
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, TextAreaField, SelectMultipleField
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    InputRequired,
)

from app.utils import (
    LabelNames,
    SubLabelsAClient,
    SubLabelsATherapist,
    SubLabelsADyad,
    SubLabelsBClient,
    SubLabelsBTherapist,
    SubLabelsBDyad,
    SubLabelsCClient,
    SubLabelsCTherapist,
    SubLabelsDClient,
    SubLabelsDTherapist,
    SubLabelsEClient,
    SubLabelsETherapist,
    SubLabelsFClient,
    LabelStrengthAClient,
    LabelStrengthATherapist,
    LabelStrengthADyad,
    LabelStrengthBClient,
    LabelStrengthBTherapist,
    LabelStrengthBDyad,
    LabelStrengthCClient,
    LabelStrengthCTherapist,
    LabelStrengthDClient,
    LabelStrengthDTherapist,
    LabelStrengthEClient,
    LabelStrengthETherapist,
    LabelStrengthFClient,
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


def create_select_field(label, choices, name, default=None):
    """Create a select field with the given label, choices, name and default value"""

    return SelectField(
        label=label,
        choices=[(choice.name, choice.value) for choice in choices],
        validators=[DataRequired()],
        name=name,
        default=default,
    )


def create_multiple_select_field_without_choices(label, name):
    """
    Create a select multiple field with the given label and name, but without choices.
    This is used for select multiple fields with dynamic choice values.
    """

    return SelectMultipleField(
        label=label,
        validators=[DataRequired()],
        name=name,
        coerce=int,
    )


def create_text_area_field(
    label, name, required_if=None, max_length=200, rows=2, cols=10
):
    """
    Create a text area field with the given label, name and max length.
    The field is required if the field with the given name is set to the given value.
    Otherwise, the field is optional.
    """

    if required_if:
        value = "other"  # value of the field that requires the text area field
        message = "If you select Other, please provide a comment."
        validators = [RequiredIf(required_if, value, message), Length(max=max_length)]
    else:
        validators = [Length(max=max_length)]
    return TextAreaField(
        label,
        validators=validators,
        name=name,
        render_kw={"rows": rows, "cols": cols},
    )


class PSAnnotationFormClient(FlaskForm):
    """Segment level annotation form of psychotherapy datasets for the client"""

    label_a = create_select_field(
        label=LabelNames.label_a_client.value,
        choices=SubLabelsAClient,
        name="label_a_client",
    )
    label_b = create_select_field(
        label=LabelNames.label_b_client.value,
        choices=SubLabelsBClient,
        name="label_b_client",
    )
    label_c = create_select_field(
        label=LabelNames.label_c_client.value,
        choices=SubLabelsCClient,
        name="label_c_client",
    )
    label_d = create_select_field(
        label=LabelNames.label_d_client.value,
        choices=SubLabelsDClient,
        name="label_d_client",
    )
    label_e = create_select_field(
        label=LabelNames.label_e_client.value,
        choices=SubLabelsEClient,
        name="label_e_client",
    )
    label_f = create_select_field(
        label=LabelNames.label_f_client.value,
        choices=SubLabelsFClient,
        name="label_f_client",
        default=SubLabelsFClient.no_change.name,
    )
    strength_a = create_select_field(
        label="Strength", choices=LabelStrengthAClient, name="strength_a_client"
    )
    strength_b = create_select_field(
        label="Strength", choices=LabelStrengthBClient, name="strength_b_client"
    )
    strength_c = create_select_field(
        label="Strength", choices=LabelStrengthCClient, name="strength_c_client"
    )
    strength_d = create_select_field(
        label="Strength", choices=LabelStrengthDClient, name="strength_d_client"
    )
    strength_e = create_select_field(
        label="Strength", choices=LabelStrengthEClient, name="strength_e_client"
    )
    strength_f = create_select_field(
        label="Strength",
        choices=LabelStrengthFClient,
        name="strength_f_client",
        default=LabelStrengthFClient.no_change.name,
    )
    comment_a = create_text_area_field(
        label="Comment", name="comment_a_client", required_if="label_a"
    )
    comment_b = create_text_area_field(
        label="Comment", name="comment_b_client", required_if="label_b"
    )
    comment_c = create_text_area_field(
        label="Comment", name="comment_c_client", required_if="label_c"
    )
    comment_d = create_text_area_field(
        label="Comment", name="comment_d_client", required_if="label_d"
    )
    comment_e = create_text_area_field(
        label="Comment", name="comment_e_client", required_if="label_e"
    )
    comment_f = create_text_area_field(label="Comment", name="comment_f_client")
    relevant_events_a = create_multiple_select_field_without_choices(
        label="Evidence", name="relevant_events_a_client"
    )
    relevant_events_b = create_multiple_select_field_without_choices(
        label="Evidence", name="relevant_events_b_client"
    )
    relevant_events_c = create_multiple_select_field_without_choices(
        label="Evidence", name="relevant_events_c_client"
    )
    relevant_events_d = create_multiple_select_field_without_choices(
        label="Evidence", name="relevant_events_d_client"
    )
    relevant_events_e = create_multiple_select_field_without_choices(
        label="Evidence", name="relevant_events_e_client"
    )
    comment_summary = create_text_area_field(
        label="Summary Comment",
        name="comment_summary_client",
        max_length=500,
        rows=3,
        cols=15,
    )
    submit = SubmitField("Submit")


class PSAnnotationFormTherapist(FlaskForm):
    """Segment level annotation form of psychotherapy datasets for the therapist"""

    label_a = create_select_field(
        label=LabelNames.label_a_therapist.value,
        choices=SubLabelsATherapist,
        name="label_a_therapist",
    )
    label_b = create_select_field(
        label=LabelNames.label_b_therapist.value,
        choices=SubLabelsBTherapist,
        name="label_b_therapist",
    )
    label_c = create_select_field(
        label=LabelNames.label_c_therapist.value,
        choices=SubLabelsCTherapist,
        name="label_c_therapist",
    )
    label_d = create_select_field(
        label=LabelNames.label_d_therapist.value,
        choices=SubLabelsDTherapist,
        name="label_d_therapist",
    )
    label_e = create_select_field(
        label=LabelNames.label_e_therapist.value,
        choices=SubLabelsETherapist,
        name="label_e_therapist",
    )
    strength_a = create_select_field(
        label="Strength", choices=LabelStrengthATherapist, name="strength_a_therapist"
    )
    strength_b = create_select_field(
        label="Strength", choices=LabelStrengthBTherapist, name="strength_b_therapist"
    )
    strength_c = create_select_field(
        label="Strength", choices=LabelStrengthCTherapist, name="strength_c_therapist"
    )
    strength_d = create_select_field(
        label="Strength", choices=LabelStrengthDTherapist, name="strength_d_therapist"
    )
    strength_e = create_select_field(
        label="Strength", choices=LabelStrengthETherapist, name="strength_e_therapist"
    )
    comment_a = create_text_area_field(
        label="Comment", name="comment_a_therapist", required_if="label_a"
    )
    comment_b = create_text_area_field(
        label="Comment", name="comment_b_therapist", required_if="label_b"
    )
    comment_c = create_text_area_field(
        label="Comment", name="comment_c_therapist", required_if="label_c"
    )
    comment_d = create_text_area_field(
        label="Comment", name="comment_d_therapist", required_if="label_d"
    )
    comment_e = create_text_area_field(
        label="Comment", name="comment_e_therapist", required_if="label_e"
    )
    relevant_events_a = create_multiple_select_field_without_choices(
        label="Evidence", name="relevant_events_a_therapist"
    )
    relevant_events_b = create_multiple_select_field_without_choices(
        label="Evidence", name="relevant_events_b_therapist"
    )
    relevant_events_c = create_multiple_select_field_without_choices(
        label="Evidence", name="relevant_events_c_therapist"
    )
    relevant_events_d = create_multiple_select_field_without_choices(
        label="Evidence", name="relevant_events_d_therapist"
    )
    relevant_events_e = create_multiple_select_field_without_choices(
        label="Evidence", name="relevant_events_e_therapist"
    )
    comment_summary = create_text_area_field(
        label="Summary Comment",
        name="comment_summary_therapist",
        max_length=500,
        rows=3,
        cols=15,
    )
    submit = SubmitField("Submit")


class PSAnnotationFormDyad(FlaskForm):
    """Segment level annotation form of psychotherapy datasets for the dyad"""

    label_a = create_select_field(
        label=LabelNames.label_a_dyad.value, choices=SubLabelsADyad, name="label_a_dyad"
    )
    label_b = create_select_field(
        label=LabelNames.label_b_dyad.value, choices=SubLabelsBDyad, name="label_b_dyad"
    )
    strength_a = create_select_field(
        label="Strength", choices=LabelStrengthADyad, name="strength_a_dyad"
    )
    strength_b = create_select_field(
        label="Strength", choices=LabelStrengthBDyad, name="strength_b_dyad"
    )
    comment_a = create_text_area_field(
        label="Comment", name="comment_a_dyad", required_if="label_a"
    )
    comment_b = create_text_area_field(
        label="Comment", name="comment_b_dyad", required_if="label_b"
    )
    comment_summary = create_text_area_field(
        label="Summary Comment",
        name="comment_summary_dyad",
        max_length=500,
        rows=3,
        cols=15,
    )
