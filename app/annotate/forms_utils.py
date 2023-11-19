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
    """Validator which makes a form field required if another field is set to a certain value or values."""

    field_flags = ("requiredif",)

    def __init__(
        self, other_field_name: str, values: list, message: str = None, *args, **kwargs
    ):
        self.other_field_name = other_field_name
        self.values = list(map(str.lower, values))
        self.message = message

    def __call__(self, form, field):
        other_field = form[self.other_field_name]
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if (other_field.data).lower() in self.values:
            super(RequiredIf, self).__call__(form, field)
        else:
            Optional().__call__(form, field)


class RequiredIfNot(InputRequired):
    """Validator which makes a form field required if another field is not set to a certain value or values."""

    # NOTE: deprecated, using JavaScript instead

    field_flags = ("requiredifnot",)

    def __init__(
        self, other_field_name: str, values: list, message: str = None, *args, **kwargs
    ):
        self.other_field_name = other_field_name
        self.values = list(map(str.lower, values))
        self.message = message

    def __call__(self, form, field):
        other_field = form[self.other_field_name]
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if (other_field.data).lower() not in self.values:
            super(RequiredIfNot, self).__call__(form, field)
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


def create_select_field_without_choices(
    label: str,
    name: str,
    data_required: bool = False,
) -> SelectField:
    """
    Create a select field with the given label and name, but without choices.
    This is used for select fields with dynamic choice values.
    Set 'data_required' to True if the field is always required.
    """

    if data_required:
        validators = [DataRequired()]
    else:
        validators = []
    return SelectField(
        label=label,
        validators=validators,
        name=name,
        coerce=int,
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
        value = ["Other"]  # value of the field that requires the text area field
        message = f"If you select {value[0]}, please provide a comment."
        validators = [RequiredIf(required_if, value, message), Length(max=max_length)]
    else:
        validators = [Length(max=max_length)]
    return TextAreaField(
        label,
        validators=validators,
        name=name,
        render_kw={"rows": rows, "cols": cols},
    )
