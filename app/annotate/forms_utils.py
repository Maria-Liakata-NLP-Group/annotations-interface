"""
Utility functions for annotation forms
"""
from wtforms import SelectField, TextAreaField, SelectMultipleField
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    InputRequired,
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


def create_select_field_without_choices(label, name, data_required=False):
    """
    Create a select field with the given label and name, but without choices.
    This is used for select fields with dynamic choice values.
    Set 'data_required' to True if the field is required.
    """

    if data_required:
        return SelectField(
            label=label,
            validators=[DataRequired()],
            name=name,
            coerce=int,
            default=None,
        )
    else:
        return SelectField(
            label=label,
            name=name,
            coerce=int,
            default=None,
        )


def create_select_multiple_field_without_choices(label, name, data_required=False):
    """
    Create a select multiple field with the given label and name, but without choices.
    This is used for select multiple fields with dynamic choice values.
    Set 'data_required' to True if the field is required.
    """

    if data_required:
        return SelectMultipleField(
            label=label,
            validators=[DataRequired()],
            name=name,
            coerce=int,
        )
    else:
        return SelectMultipleField(
            label=label,
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
