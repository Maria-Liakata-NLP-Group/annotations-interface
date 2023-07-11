"""
Miscellaneous utility functions for the annotate blueprint
"""
from datetime import datetime


def split_dialog_turns(dialog_turns, time_interval=300):
    """
    Split a list of dialog turns into time sections, identified by the timestamp.
    The dialog turns must be sorted by timestamp in ascending order.

    Parameters
    ----------
    dialog_turns : list
        A list of PSDialogTurn objects
    time_interval : int
        The time interval in seconds (default is 300, i.e. 5 minutes)

    Returns
    -------
    sections : list
        A list of sections, each section is a list of PSDialogTurn objects
    """
    sections = []
    section = [dialog_turns[0]]
    # "timestamp" is a time object, so we need to convert it to
    # a datetime object to get a time difference
    current_date = datetime.now().date()
    datetime1 = datetime.combine(current_date, section[0].timestamp)
    for dialog_turn in dialog_turns[1:]:
        datetime2 = datetime.combine(current_date, dialog_turn.timestamp)
        if (datetime2 - datetime1).total_seconds() < time_interval:
            section.append(dialog_turn)
        else:
            sections.append(section)
            section = [dialog_turn]
            datetime1 = datetime.combine(current_date, section[0].timestamp)
    sections.append(section)
    return sections


def get_events_from_sections(sections):
    """
    Get the events corresponding to each section of dialog turns.

    Parameters
    ----------
    sections : list
        A list of sections, each section is a list of PSDialogTurn objects

    Returns
    -------
    events : list
        A list of sections, each section is a list of PSDialogEvent objects
    """
    events = []
    for section in sections:
        events.append([dialog_turn.dialog_events for dialog_turn in section])
    return events
