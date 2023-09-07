from app.utils import (
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
)


def create_segment_level_annotation_client():
    """
    Create a dictionary with the data for a segment level annotation for the client.
    """

    data = {
        "label_a_client": SubLabelsAClient.excitement.name,
        "label_b_client": SubLabelsBClient.security.name,
        "label_c_client": SubLabelsCClient.esteem.name,
        "label_d_client": SubLabelsDClient.positive.name,
        "label_e_client": SubLabelsEClient.insight.name,
        "strength_a_client": LabelStrength.high.name,
        "strength_b_client": LabelStrength.medium.name,
        "strength_c_client": LabelStrength.low.name,
        "strength_d_client": LabelStrength.high.name,
        "strength_e_client": LabelStrength.medium.name,
        "comment_a_client": "test comment A",
        "comment_b_client": "test comment B",
        "comment_c_client": "test comment C",
        "comment_d_client": "test comment D",
        "comment_e_client": "test comment E",
        "submit_form_client": "Submit",  # this is the name of the submit button and identifies the form
    }
    return data


def create_segment_level_annotation_therapist():
    """
    Create a dictionary with the data for a segment level annotation for the therapist.
    """

    data = {
        "label_a_therapist": SubLabelsATherapist.emotional.name,
        "label_b_therapist": SubLabelsBTherapist.reframing.name,
        "label_c_therapist": SubLabelsCTherapist.exploration.name,
        "label_d_therapist": SubLabelsDTherapist.restructuring.name,
        "label_e_therapist": SubLabelsETherapist.general_helpfulness.name,
        "strength_a_therapist": LabelStrength.high.name,
        "strength_b_therapist": LabelStrength.medium.name,
        "strength_c_therapist": LabelStrength.low.name,
        "strength_d_therapist": LabelStrength.high.name,
        "strength_e_therapist": LabelStrength.medium.name,
        "comment_a_therapist": "test comment A",
        "comment_b_therapist": "test comment B",
        "comment_c_therapist": "test comment C",
        "comment_d_therapist": "test comment D",
        "comment_e_therapist": "test comment E",
        "submit_form_therapist": "Submit",  # this is the name of the submit button and identifies the form
    }
    return data
