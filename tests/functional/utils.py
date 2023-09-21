from app.utils import (
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
        "label_f_client": SubLabelsFClient.switch.name,
        "strength_a_client": LabelStrengthAClient.highly_maladaptive.name,
        "strength_b_client": LabelStrengthBClient.very_maladaptive.name,
        "strength_c_client": LabelStrengthCClient.moderately_adaptive.name,
        "strength_d_client": LabelStrengthDClient.very_adaptive.name,
        "strength_e_client": LabelStrengthEClient.low_recognition.name,
        "strength_f_client": LabelStrengthFClient.some_improvement.name,
        "comment_a_client": "test comment A",
        "comment_b_client": "test comment B",
        "comment_c_client": "test comment C",
        "comment_d_client": "test comment D",
        "comment_e_client": "test comment E",
        # TODO: create function that retrieves the event IDs from the database so that they are not hard-coded
        "relevant_events_a_client": 2,  # note this is the event ID, not the event number (shown in the UI)
        "relevant_events_b_client": 2,
        "relevant_events_c_client": 2,
        "relevant_events_d_client": 2,
        "relevant_events_e_client": 2,
        "start_event_f_client": 2,
        "end_event_f_client": 4,
        "comment_summary_client": "test comment summary client",
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
        "strength_a_therapist": LabelStrengthATherapist.low.name,
        "strength_b_therapist": LabelStrengthBTherapist.medium.name,
        "strength_c_therapist": LabelStrengthCTherapist.high.name,
        "strength_d_therapist": LabelStrengthDTherapist.low.name,
        "strength_e_therapist": LabelStrengthETherapist.medium.name,
        "comment_a_therapist": "test comment A",
        "comment_b_therapist": "test comment B",
        "comment_c_therapist": "test comment C",
        "comment_d_therapist": "test comment D",
        "comment_e_therapist": "test comment E",
        "relevant_events_a_therapist": 1,  # note this is the event ID, not the event number (shown in the UI)
        "relevant_events_b_therapist": 1,
        "relevant_events_c_therapist": 1,
        "relevant_events_d_therapist": 1,
        "relevant_events_e_therapist": 1,
        "comment_summary_therapist": "test comment summary therapist",
        "submit_form_therapist": "Submit",  # this is the name of the submit button and identifies the form
    }
    return data


def create_segment_level_annotation_dyad():
    """
    Create a dictionary with the data for a segment level annotation for the dyad.
    """

    data = {
        "label_a_dyad": SubLabelsADyad.tasks_goals.name,
        "label_b_dyad": SubLabelsBDyad.withdrawal.name,
        "strength_a_dyad": LabelStrengthADyad.low.name,
        "strength_b_dyad": LabelStrengthBDyad.medium.name,
        "comment_a_dyad": "test comment A",
        "comment_b_dyad": "test comment B",
        "relevant_events_a_dyad": 1,  # note this is the event ID, not the event number (shown in the UI)
        "relevant_events_b_dyad": 1,
        "comment_summary_dyad": "test comment summary dyad",
        "submit_form_dyad": "Submit",  # this is the name of the submit button and identifies the form
    }
    return data
