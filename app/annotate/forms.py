"""
Annotation forms for the app
"""
from flask_wtf import FlaskForm
from wtforms import SubmitField
from app.annotate.forms_utils import (
    create_select_field,
    create_select_field_without_choices,
    create_select_multiple_field_without_choices,
    create_text_area_field,
)
from app.utils import (
    LabelNamesTherapist,
    LabelNamesDyad,
    SubLabelsATherapist,
    SubLabelsADyad,
    SubLabelsBTherapist,
    SubLabelsBDyad,
    SubLabelsCTherapist,
    SubLabelsDTherapist,
    SubLabelsETherapist,
    LabelStrengthATherapist,
    LabelStrengthADyad,
    LabelStrengthBTherapist,
    LabelStrengthBDyad,
    LabelStrengthCTherapist,
    LabelStrengthDTherapist,
    LabelStrengthETherapist,
)


class PSAnnotationForm(FlaskForm):
    """Generic segment level annotation form of psychotherapy datasets"""

    # NOTE: currently this form is not used. It is kept here for future reference.

    # TODO: finish writing this class when there is time. The purpose of this class is
    # to create the annotation forms dynamically, based on the annotation schema on the
    # database, without hard-coding the fields in the form.

    def __init__(self):
        self.prefix_name = "name_"  # the prefix of the field group names
        self.prefix_label = "label_"  # the prefix of the label fields
        self.prefix_sub_label = "sub_label_"  # the prefix of the sublabel fields
        self.suffix_additional = "_add"  # the suffix of the additional label fields
        self.prefix_scale = "scale_"  # the prefix of the scale fields
        self.prefix_comment = "comment_"  # the prefix of the comment fields
        self.suffix_entity = (
            "_who"  # this tags the entity of the label, e.g. client, therapist, dyad
        )

    def _find_next_letter(self):
        """Return the next letter of the alphabet to be used in the field group names"""

        # check the existing names of the field groups
        attributes = self.__dict__.keys()
        names = [
            attribute
            for attribute in attributes
            if attribute.startswith(self.prefix_name)
        ]
        # the field groups are named "name_a", "name_b", "name_c", etc.
        # find the last letter of the alphabet that is used in the field group names
        if not names:
            return "a"
        names.sort()
        last_name = names[-1]
        last_letter = last_name[-1]
        return chr(ord(last_letter + 1))

    def _create_new_name(self, new_letter, name):
        """Create the new name for the field group"""

        new_name = self.prefix_name + new_letter
        setattr(self, new_name, name)

    def _create_new_label_field(self, new_letter, suffix, data_required=True):
        """Create the new label field"""

        new_label_field = self.prefix_label + new_letter
        setattr(
            self,
            new_label_field,
            create_select_field_without_choices(
                label="(" + new_letter.upper() + ")",
                name=new_label_field + suffix,
                data_required=data_required,
            ),
        )

    def _create_new_sub_label_fields(
        self, new_letter, suffix, num_sub_labels, data_required=True
    ):
        """Create the new sub label fields"""

        new_sub_label_field = self.prefix_sub_label + new_letter
        for i in range(1, num_sub_labels + 1):
            setattr(
                self,
                new_sub_label_field + "_" + str(i),
                create_select_field_without_choices(
                    label=None,
                    name=new_sub_label_field + "_" + str(i) + suffix,
                    data_required=data_required,
                ),
            )

    def _create_new_scale_fields(
        self, new_letter, suffix, label_scales, data_required=True
    ):
        """Create the new scale fields"""

        new_scale_field = self.prefix_scale + new_letter
        for i, scale in enumerate(label_scales):
            setattr(
                self,
                new_scale_field + "_" + str(i + 1),
                create_select_field_without_choices(
                    label=scale,
                    name=new_scale_field + "_" + str(i + 1) + suffix,
                    data_required=data_required,
                ),
            )

    def create_new_fields_group(
        self,
        name,
        num_sub_labels,
        label_scales,
        label_scales_required=True,
        additional=False,
    ):
        """
        Create a new group of fields for the given name and number of sub labels.
        The new fields are added to the annotation form.

        Parameters
        ----------
        name : str
            The name of the field group. This should be the name of a parent label (i.e.
            a label that has child labels but no parent label) in the database (e.g. "Wish"
            or "Moment of Change" for the client).
        num_sub_labels : int
            The number of sub labels of the parent label. This depends on the depth of the
            annotation schema for the given parent label.
        """
        next_letter = self._find_next_letter()

        # create the new name for the field group
        self._create_new_name(next_letter, name)

        # create the new label field
        self._create_new_label_field(next_letter, suffix=self.suffix_entity)

        # create the new sub label fields
        self._create_new_sub_label_fields(
            next_letter, suffix=self.suffix_entity, num_sub_labels=num_sub_labels
        )

        # create the new scale fields
        self._create_new_scale_fields(
            next_letter,
            suffix=self.suffix_entity,
            label_scales=label_scales,
            data_required=label_scales_required,
        )


class PSAnnotationFormClient(FlaskForm):
    """Segment level annotation form of psychotherapy datasets for the client"""

    # Label A
    # -------
    name_a = "Wish".strip().capitalize()
    title_a = "(A) " + name_a
    label_a = create_select_field_without_choices(
        label="Choose one",
        name="label_a_client",
        data_required=True,
    )
    sub_label_a_1 = create_select_field_without_choices(
        label="Choose one",
        name="sub_label_a_1_client",
        required_if_not="label_a",
    )
    scale_a_1 = create_select_field_without_choices(
        label="Level".strip().capitalize(),
        name="scale_a_1_client",
        data_required=True,
    )
    scale_a_2 = create_select_field_without_choices(
        label="Adaptivity".strip().capitalize(),
        name="scale_a_2_client",
        data_required=True,
    )
    evidence_a = create_select_multiple_field_without_choices(
        label="Evidence",
        name="evidence_a_client",
        data_required=True,
    )
    comment_a = create_text_area_field(
        label="Comment",
        name="comment_a_client",
        required_if="label_a",
    )

    # Label A - additional
    # --------------------
    label_a_add = create_select_field_without_choices(
        label="Choose one",
        name="label_a_client_add",
    )
    sub_label_a_1_add = create_select_field_without_choices(
        label="Choose one",
        name="sub_label_a_1_client_add",
    )
    scale_a_1_add = create_select_field_without_choices(
        label="Level".strip().capitalize(),
        name="scale_a_1_client_add",
    )
    scale_a_2_add = create_select_field_without_choices(
        label="Adaptivity".strip().capitalize(),
        name="scale_a_2_client_add",
    )
    evidence_a_add = create_select_multiple_field_without_choices(
        label="Evidence",
        name="evidence_a_client_add",
    )
    comment_a_add = create_text_area_field(
        label="Comment",
        name="comment_a_client_add",
        required_if="label_a_add",
    )

    # Label B
    # -------
    name_b = "Response of Other".strip().capitalize()
    title_b = "(B) " + name_b
    label_b = create_select_field_without_choices(
        label="Choose one",
        name="label_b_client",
        data_required=True,
    )
    sub_label_b_1 = create_select_field_without_choices(
        label="Choose one",
        name="sub_label_b_1_client",
        data_required=True,
    )
    scale_b_1 = create_select_field_without_choices(
        label="Level".strip().capitalize(),
        name="scale_b_1_client",
        data_required=True,
    )
    scale_b_2 = create_select_field_without_choices(
        label="Adaptivity".strip().capitalize(),
        name="scale_b_2_client",
        data_required=True,
    )
    evidence_b = create_select_multiple_field_without_choices(
        label="Evidence",
        name="evidence_b_client",
        data_required=True,
    )
    comment_b = create_text_area_field(
        label="Comment",
        name="comment_b_client",
        required_if="label_b",
    )

    # Label B - additional
    # --------------------
    label_b_add = create_select_field_without_choices(
        label="Choose one",
        name="label_b_client_add",
    )
    sub_label_b_1_add = create_select_field_without_choices(
        label="Choose one",
        name="sub_label_b_1_client_add",
    )
    scale_b_1_add = create_select_field_without_choices(
        label="Level".strip().capitalize(),
        name="scale_b_1_client_add",
    )
    scale_b_2_add = create_select_field_without_choices(
        label="Adaptivity".strip().capitalize(),
        name="scale_b_2_client_add",
    )
    evidence_b_add = create_select_multiple_field_without_choices(
        label="Evidence",
        name="evidence_b_client_add",
    )
    comment_b_add = create_text_area_field(
        label="Comment",
        name="comment_b_client_add",
        required_if="label_b_add",
    )

    # Label C
    # -------
    name_c = "Response of Self".strip().capitalize()
    title_c = "(C) " + name_c
    label_c = create_select_field_without_choices(
        label="Choose one",
        name="label_c_client",
        data_required=True,
    )
    sub_label_c_1 = create_select_field_without_choices(
        label="Choose one",
        name="sub_label_c_1_client",
        data_required=True,
    )
    scale_c_1 = create_select_field_without_choices(
        label="Level".strip().capitalize(),
        name="scale_c_1_client",
        data_required=True,
    )
    scale_c_2 = create_select_field_without_choices(
        label="Adaptivity".strip().capitalize(),
        name="scale_c_2_client",
        data_required=True,
    )
    evidence_c = create_select_multiple_field_without_choices(
        label="Evidence",
        name="evidence_c_client",
        data_required=True,
    )
    comment_c = create_text_area_field(
        label="Comment",
        name="comment_c_client",
        required_if="label_c",
    )

    # Label C - additional
    # --------------------
    label_c_add = create_select_field_without_choices(
        label="Choose one",
        name="label_c_client_add",
    )
    sub_label_c_1_add = create_select_field_without_choices(
        label="Choose one",
        name="sub_label_c_1_client_add",
    )
    scale_c_1_add = create_select_field_without_choices(
        label="Level".strip().capitalize(),
        name="scale_c_1_client_add",
    )
    scale_c_2_add = create_select_field_without_choices(
        label="Adaptivity".strip().capitalize(),
        name="scale_c_2_client_add",
    )
    evidence_c_add = create_select_multiple_field_without_choices(
        label="Evidence",
        name="evidence_c_client_add",
    )
    comment_c_add = create_text_area_field(
        label="Comment",
        name="comment_c_client_add",
        required_if="label_c_add",
    )

    # Label D
    # -------
    name_d = "Emotional experiencing and regulation".strip().capitalize()
    title_d = "(D) " + name_d
    label_d = create_select_field_without_choices(
        label="Choose one",
        name="label_d_client",
        data_required=True,
    )
    scale_d_1 = create_select_field_without_choices(
        label="Arousal level".strip().capitalize(),
        name="scale_d_1_client",
        data_required=True,
    )
    scale_d_2 = create_select_field_without_choices(
        label="Adaptivity".strip().capitalize(),
        name="scale_d_2_client",
        data_required=True,
    )
    evidence_d = create_select_multiple_field_without_choices(
        label="Evidence",
        name="evidence_d_client",
        data_required=True,
    )
    comment_d = create_text_area_field(
        label="Comment",
        name="comment_d_client",
        required_if="label_d",
    )

    # Label D - additional
    # --------------------
    label_d_add = create_select_field_without_choices(
        label="Choose one",
        name="label_d_client_add",
    )
    scale_d_1_add = create_select_field_without_choices(
        label="Arousal level".strip().capitalize(),
        name="scale_d_1_client_add",
    )
    scale_d_2_add = create_select_field_without_choices(
        label="Adaptivity".strip().capitalize(),
        name="scale_d_2_client_add",
    )
    evidence_d_add = create_select_multiple_field_without_choices(
        label="Evidence",
        name="evidence_d_client_add",
    )
    comment_d_add = create_text_area_field(
        label="Comment",
        name="comment_d_client_add",
        required_if="label_d_add",
    )

    # Label E
    # -------
    name_e = "Insight".strip().capitalize()
    title_e = "(E) " + name_e
    scale_e_1 = create_select_field_without_choices(
        label="Recognition".strip().capitalize(),
        name="scale_e_1_client",
        data_required=True,
    )
    evidence_e = create_select_multiple_field_without_choices(
        label="Evidence",
        name="evidence_e_client",
        data_required=True,
    )
    comment_e = create_text_area_field(
        label="Comment",
        name="comment_e_client",
    )

    # Label E - additional
    # --------------------
    scale_e_1_add = create_select_field_without_choices(
        label="Recognition".strip().capitalize(),
        name="scale_e_1_client_add",
    )
    evidence_e_add = create_select_multiple_field_without_choices(
        label="Evidence",
        name="evidence_e_client_add",
    )
    comment_e_add = create_text_area_field(
        label="Comment",
        name="comment_e_client_add",
    )

    # Label F
    # -------
    name_f = "Moment of Change".strip().capitalize()
    title_f = "(F) " + name_f
    label_f = create_select_field_without_choices(
        label="Choose one",
        name="label_f_client",
        data_required=True,
    )
    scale_f_1 = create_select_field_without_choices(
        label="Deterioration".strip().capitalize(),
        name="scale_f_1_client",
    )
    start_event_f = create_select_field_without_choices(
        label="Start",
        name="start_event_f_client",
    )
    end_event_f = create_select_field_without_choices(
        label="End",
        name="end_event_f_client",
    )
    comment_f = create_text_area_field(
        label="Comment",
        name="comment_f_client",
    )

    # Summary comment
    # ---------------
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
        label=LabelNamesTherapist.label_a.value,
        choices=SubLabelsATherapist,
        name="label_a_therapist",
    )
    label_b = create_select_field(
        label=LabelNamesTherapist.label_b.value,
        choices=SubLabelsBTherapist,
        name="label_b_therapist",
    )
    label_c = create_select_field(
        label=LabelNamesTherapist.label_c.value,
        choices=SubLabelsCTherapist,
        name="label_c_therapist",
    )
    label_d = create_select_field(
        label=LabelNamesTherapist.label_d.value,
        choices=SubLabelsDTherapist,
        name="label_d_therapist",
    )
    label_e = create_select_field(
        label=LabelNamesTherapist.label_e.value,
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
    relevant_events_a = create_select_multiple_field_without_choices(
        label="Evidence", name="relevant_events_a_therapist"
    )
    relevant_events_b = create_select_multiple_field_without_choices(
        label="Evidence", name="relevant_events_b_therapist"
    )
    relevant_events_c = create_select_multiple_field_without_choices(
        label="Evidence", name="relevant_events_c_therapist"
    )
    relevant_events_d = create_select_multiple_field_without_choices(
        label="Evidence", name="relevant_events_d_therapist"
    )
    relevant_events_e = create_select_multiple_field_without_choices(
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
        label=LabelNamesDyad.label_a.value, choices=SubLabelsADyad, name="label_a_dyad"
    )
    label_b = create_select_field(
        label=LabelNamesDyad.label_b.value, choices=SubLabelsBDyad, name="label_b_dyad"
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
    relevant_events_a = create_select_multiple_field_without_choices(
        label="Evidence", name="relevant_events_a_dyad"
    )
    relevant_events_b = create_select_multiple_field_without_choices(
        label="Evidence", name="relevant_events_b_dyad"
    )
    comment_summary = create_text_area_field(
        label="Summary Comment",
        name="comment_summary_dyad",
        max_length=500,
        rows=3,
        cols=15,
    )
