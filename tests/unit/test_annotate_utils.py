"""
Unit tests for the utilities module in the annotate blueprint.
"""
from datetime import time
from app.models import PSDialogTurn, PSDialogEvent, ClientAnnotationSchema
from app.annotate.utils import (
    split_dialog_turns,
    get_events_from_segments,
)
from app.annotate.forms import PSAnnotationForm
import pytest


def create_dialog_turns():
    """
    Create a list of dialog turns for testing purposes.
    """
    dialog_turns = []
    dialog_turns.append(
        PSDialogTurn(
            id=1,
            timestamp=time(0, 0, 10),
        )
    )
    dialog_turns.append(
        PSDialogTurn(
            id=2,
            timestamp=time(0, 2, 20),
        )
    )
    dialog_turns.append(
        PSDialogTurn(
            id=3,
            timestamp=time(0, 4, 40),
        )
    )
    dialog_turns.append(
        PSDialogTurn(
            id=4,
            timestamp=time(0, 5, 30),
        )
    )
    dialog_turns.append(
        PSDialogTurn(
            id=5,
            timestamp=time(0, 10, 00),
        )
    )
    dialog_turns.append(
        PSDialogTurn(
            id=6,
            timestamp=time(0, 15, 30),
        )
    )
    dialog_turns.append(
        PSDialogTurn(
            id=7,
            timestamp=time(0, 22, 10),
        )
    )
    dialog_turns.append(
        PSDialogTurn(
            id=8,
            timestamp=time(0, 23, 40),
        )
    )
    return dialog_turns


@pytest.mark.order(3)
@pytest.mark.dependency()
def test_split_dialog_turns():
    """Test the split_dialog_turns() function."""
    dialog_turns = create_dialog_turns()
    segments = split_dialog_turns(dialog_turns, time_interval=300)
    expected_segments = [
        [dialog_turns[0], dialog_turns[1], dialog_turns[2]],
        [dialog_turns[3], dialog_turns[4]],
        [dialog_turns[5]],
        [dialog_turns[6], dialog_turns[7]],
    ]
    assert segments == expected_segments


@pytest.mark.dependency(depends=["test_split_dialog_turns"])
def test_get_events_from_segments(insert_ps_dialog_turns):
    """Test the get_events_from_segments() function."""
    dialog_turns = PSDialogTurn.query.all()
    segments = split_dialog_turns(dialog_turns, time_interval=300)
    events = get_events_from_segments(segments)
    assert len(segments) == len(events)
    # check that that all events in a given segment are instances of the PSDialogEvent class
    for segment in events:
        assert all(isinstance(event, PSDialogEvent) for event in segment)


def test_get_annotation_label_children(new_ps_annotation_schema_client):
    """Test the get_label_children() method of the AnnotationSchemaMixin class."""

    # check "tests/data/annotation_schema/client.json"
    label = "To avoid conflict"
    parent_label = "Wish"
    child_label_names = ["To avoid conflict", "To compromise", "To be flexible"]
    client_annotation_schema = ClientAnnotationSchema()
    child_labels = client_annotation_schema.get_label_children(
        label, parent_label, append_placeholder=False
    )
    # extract the names of the child labels (list of tuples where name is second element)
    child_label_names_extracted = [child_label[1] for child_label in child_labels]
    # sort the lists to make sure they are in the same order, and apply strip() and capitalize()
    child_label_names = sorted(
        [
            child_label_name.strip().capitalize()
            for child_label_name in child_label_names
        ]
    )
    child_label_names_extracted = sorted(
        [
            child_label_name.strip().capitalize()
            for child_label_name in child_label_names_extracted
        ]
    )
    assert child_label_names == child_label_names_extracted


def test_find_annotation_parent_label_depth():
    """Test the find_parent_label_depth() method of the AnnotationSchemaMixin class."""

    client_annotation_schema = ClientAnnotationSchema()
    # check "tests/data/annotation_schema/client.json"
    assert client_annotation_schema.find_parent_label_depth("Wish") == 2
    assert client_annotation_schema.find_parent_label_depth("Insight") == 0
    assert client_annotation_schema.find_parent_label_depth("Moment of change") == 1


def test_get_annotation_label_scales():
    """Test the get_label_scales() method of the AnnotationSchemaMixin class."""

    client_annotation_schema = ClientAnnotationSchema()
    # check "tests/data/annotation_schema/scales/client.json"
    scales = client_annotation_schema.get_label_scales(
        "Wish", "Level", append_placeholder=False
    )
    expected_scales = [
        (1, "1. Not present".strip().capitalize()),
        (2, "2. Somewhat present".strip().capitalize()),
        (3, "3. Moderately present".strip().capitalize()),
        (4, "4. Very present".strip().capitalize()),
        (5, "5. Highly present".strip().capitalize()),
    ]
    assert scales == expected_scales


# skip this test for now until the PSAnnotationForm class is refactored
@pytest.mark.skip(reason="PSAnnotationForm class needs to be refactored")
def test_ps_annotation_form():
    """Test the PSAnnotationForm class."""

    form = PSAnnotationForm()

    # test the _find_next_letter() method
    assert form._find_next_letter() == "a"

    # test the create_new_fields_group() method
    parent_label = "labelA1"
    num_sub_labels = 2
    label_scales = ["scale1", "scale2"]
    form.create_new_fields_group(parent_label, num_sub_labels, label_scales)
    # check that the new group name was created
    assert "name_a" in form.__dict__.keys()
    assert form.name_a == "labelA1"
    # check that the label was created
    assert "label_a" in form.__dict__.keys()
    assert form.label_a.name == "label_a_who"  # this is the HTML name
    assert form.label_a.kwargs["label"] == "(A)"  # this is the form field label
    # check that two sub-labels were created
    sub_labels = [
        attribute for attribute in form.__dict__.keys() if "sub_label_" in attribute
    ]
    assert sub_labels == ["sub_label_a_1", "sub_label_a_2"]
    assert form.sub_label_a_1.name == "sub_label_a_1_who"  # this is the HTML name
    # test that they have no label
    assert form.sub_label_a_1.kwargs["label"] is None
    # check that two scales were created
    scales = [attribute for attribute in form.__dict__.keys() if "scale_" in attribute]
    assert scales == ["scale_a_1", "scale_a_2"]
    assert form.scale_a_1.name == "scale_a_1_who"  # this is the HTML name
    # test that they have the correct label
    assert form.scale_a_1.kwargs["label"] == "scale1"
