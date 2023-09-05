from app.utils import (
    LabelScale,
    SubLabelsA,
    SubLabelsB,
    SubLabelsC,
    SubLabelsD,
    SubLabelsE,
)


def create_segment_level_annotation(speaker):
    """
    Create a dictionary with the data for a segment level psychotherapy annotation form

    Args:
        speaker (str): the speaker of the dialog turn. One of 'client' or 'therapist'

    Returns:
        data (dict): the data for the form
    """
    data = {
        f"label_a_{speaker}": SubLabelsA.excitement.name,
        f"label_b_{speaker}": SubLabelsB.sublabel2.name,
        f"label_c_{speaker}": SubLabelsC.sublabel3.name,
        f"label_d_{speaker}": SubLabelsD.sublabel4.name,
        f"label_e_{speaker}": SubLabelsE.other.name,
        f"strength_a_{speaker}": LabelScale.high.name,
        f"strength_b_{speaker}": LabelScale.medium.name,
        f"strength_c_{speaker}": LabelScale.low.name,
        f"strength_d_{speaker}": LabelScale.high.name,
        f"strength_e_{speaker}": LabelScale.medium.name,
        f"comment_a_{speaker}": "test comment A",
        f"comment_b_{speaker}": "test comment B",
        f"comment_c_{speaker}": "test comment C",
        f"comment_d_{speaker}": "test comment D",
        f"comment_e_{speaker}": "test comment E",
        f"submit_form_{speaker}": "Submit",  # this is the name of the submit button and identifies the form
    }
    return data
