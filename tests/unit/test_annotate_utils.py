"""
Unit tests for the utilities module in the annotate blueprint.
"""
from datetime import time
from app.models import PSDialogTurn, PSDialogEvent
from app.annotate.utils import split_dialog_turns, get_events_from_sections
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


@pytest.mark.dependency()
def test_split_dialog_turns():
    """Test the split_dialog_turns() function."""
    dialog_turns = create_dialog_turns()
    sections = split_dialog_turns(dialog_turns, time_interval=300)
    expected_sections = [
        [dialog_turns[0], dialog_turns[1], dialog_turns[2]],
        [dialog_turns[3], dialog_turns[4]],
        [dialog_turns[5]],
        [dialog_turns[6], dialog_turns[7]],
    ]
    assert sections == expected_sections


@pytest.mark.dependency(depends=["test_split_dialog_turns"])
def test_get_events_from_sections(insert_ps_dialog_turns):
    """Test the get_events_from_sections() function."""
    dialog_turns = PSDialogTurn.query.all()
    sections = split_dialog_turns(dialog_turns, time_interval=300)
    events = get_events_from_sections(sections)
    assert len(sections) == len(events)
    # check that that all events in a given section are instances of the PSDialogEvent class
    for section in events:
        assert all(isinstance(event, PSDialogEvent) for event in section)
