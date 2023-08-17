"""
Miscellaneous utility functions for the annotate blueprint
"""
from datetime import datetime
import itertools
from flask import url_for
from flask_login import current_user
from app.utils import Speaker
from sqlalchemy import desc


def split_dialog_turns(dialog_turns, time_interval=300):
    """
    Split a list of dialog turns into time segments, identified by the timestamp.
    The dialog turns must be sorted by timestamp in ascending order.

    Parameters
    ----------
    dialog_turns : list
        A list of PSDialogTurn objects
    time_interval : int
        The time interval in seconds (default is 300, i.e. 5 minutes)

    Returns
    -------
    segments : list
        A list of segments, each segment is a list of PSDialogTurn objects
    """
    segments = []
    segment = [dialog_turns[0]]
    # "timestamp" is a time object, so we need to convert it to
    # a datetime object to get a time difference
    current_date = datetime.now().date()
    datetime1 = datetime.combine(current_date, segment[0].timestamp)
    for dialog_turn in dialog_turns[1:]:
        datetime2 = datetime.combine(current_date, dialog_turn.timestamp)
        if (datetime2 - datetime1).total_seconds() < time_interval:
            segment.append(dialog_turn)
        else:
            segments.append(segment)
            segment = [dialog_turn]
            datetime1 = datetime.combine(current_date, segment[0].timestamp)
    segments.append(segment)
    return segments


def get_events_from_segments(segments):
    """
    Get the events corresponding to each segment of dialog turns.
    The events are sorted by event number in ascending order (i.e. in time order).

    Parameters
    ----------
    segments : list
        A list of segments, each segment is a list of PSDialogTurn objects

    Returns
    -------
    events : list
        A list of segments, each segment is a list of PSDialogEvent objects
    """
    events = []
    for segment in segments:
        events.append(
            list(
                itertools.chain.from_iterable(
                    dialog_turn.dialog_events.order_by("event_n").all()
                    for dialog_turn in segment
                )
            )
        )
    return events


def get_page_items(page, events, dataset_id):
    """
    Get the events for the current page and the urls for the pager.

    Parameters
    ----------
    page : int
        The current page number
    events : list
        A list of segments, each segment is a list of PSDialogEvent objects
    dataset_id : int
        The id of the dataset

    Returns
    -------
    page_items : list
        A list of PSDialogEvent objects for the current page
    next_url : str
        The url for the next page
    prev_url : str
        The url for the previous page
    first_url : str
        The url for the first page
    last_url : str
        The url for the last page
    total_pages : int
        The total number of pages
    """
    page_items = events[page - 1]  # get the events for the current page
    total_pages = len(events)  # total number of pages
    has_prev = page > 1  # check if there is a previous page
    has_next = page < total_pages  # check if there is a next page
    is_first = page == 1  # check if the current page is the first page
    is_last = page == total_pages  # check if the current page is the last page
    # create the urls for the pager
    if has_prev:
        prev_url = url_for("annotate.annotate_ps", dataset_id=dataset_id, page=page - 1)
    else:
        prev_url = None
    if has_next:
        next_url = url_for("annotate.annotate_ps", dataset_id=dataset_id, page=page + 1)
    else:
        next_url = None
    if is_first:
        first_url = None
    else:
        first_url = url_for("annotate.annotate_ps", dataset_id=dataset_id, page=1)
    if is_last:
        last_url = None
    else:
        last_url = url_for(
            "annotate.annotate_ps", dataset_id=dataset_id, page=total_pages
        )
    return page_items, next_url, prev_url, first_url, last_url, total_pages


def fetch_dialog_turn_annotations(dialog_turns: list, speaker: Speaker):
    """
    Fetch the the annotations for the dialog turns and only return the annotation
    with the latest timestamp.

    Parameters
    ----------
    dialog_turns : list
        A list of PSDialogTurn objects
    speaker : Speaker
        The speaker the annotation is for (client or therapist)

    Returns
    -------
    annotations : PSDialogTurnAnnotation
        The annotation with the latest timestamp if it exists, otherwise None.
        The "label_*" and "strength_*" attributes are converted to their corresponding Enum values.
    """

    annotations = []
    for dialog_turn in dialog_turns:
        annotation = (
            dialog_turn.annotations.filter_by(id_user=current_user.id, speaker=speaker)
            .order_by(desc("timestamp"))
            .first()
        )
        if annotation:
            annotations.append(annotation)
    # sort the annotations by timestamp in ascending order
    if annotations:
        annotations.sort(key=lambda x: x.timestamp)
        annotation = annotations[-1]
        # convert the "label_*" and "strength_*" attributes to their corresponding Enum values
        # this is needed so that the annotations form can be pre-populated correctly
        for attr in annotation.__dict__.keys():
            if attr.startswith("label_"):
                setattr(annotation, attr, getattr(annotation, attr).value)
            elif attr.startswith("strength_"):
                setattr(annotation, attr, getattr(annotation, attr).value)
    else:
        annotation = None
    return annotation
