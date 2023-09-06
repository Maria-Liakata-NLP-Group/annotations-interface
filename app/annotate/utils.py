"""
Miscellaneous utility functions for the annotate blueprint
"""
from datetime import datetime
import itertools
from flask import url_for
from flask_login import current_user
from app.utils import Speaker
from sqlalchemy import desc
from app.models import PSDialogTurnAnnotation
from app import db


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
        )  # for this dialog turn, get the annotation with the latest timestamp
        if annotation:
            annotations.append(annotation)
    if annotations:
        # sort the annotations by timestamp in ascending order and get the last one
        annotations.sort(key=lambda x: x.timestamp)
        annotation = annotations[-1]
        # convert the "label_*" and "strength_*" attributes to their corresponding Enum names
        # this is needed so that the annotations form can be pre-populated correctly
        for attr in annotation.__dict__.keys():
            if attr.startswith("label_") and getattr(annotation, attr) is not None:
                setattr(annotation, attr, getattr(annotation, attr).name)
            elif attr.startswith("strength_"):
                setattr(annotation, attr, getattr(annotation, attr).name)
    else:
        annotation = None
    return annotation


def new_dialog_turn_annotation_to_db(form, speaker, dataset_id, dialog_turn_ids):
    """
    Create a new psychotherapy dialog turn annotation object and add it to the database session.
    Loops through the dialog turn IDs and creates a new annotation for each one.

    Parameters
    ----------
    form : PSAnnotationFormClient or PSAnnotationFormTherapist
        The form containing the annotation data
    speaker : Speaker
        The speaker the annotation is for (client or therapist)
    dataset_id : int
        The id of the dataset the dialog turns belong to
    dialog_turn_ids : list
        A list of dialog turn IDs
    """
    if speaker == Speaker.client:
        for dialog_turn_id in dialog_turn_ids:
            dialog_turn_annotation = PSDialogTurnAnnotation(
                label_a_client=form.label_a_client.data,
                label_b_client=form.label_b_client.data,
                label_c_client=form.label_c_client.data,
                label_d=form.label_d.data,
                label_e=form.label_e.data,
                strength_a=form.strength_a.data,
                strength_b=form.strength_b.data,
                strength_c=form.strength_c.data,
                strength_d=form.strength_d.data,
                strength_e=form.strength_e.data,
                comment_a=form.comment_a.data,
                comment_b=form.comment_b.data,
                comment_c=form.comment_c.data,
                comment_d=form.comment_d.data,
                comment_e=form.comment_e.data,
                speaker=speaker,
                id_user=current_user.id,
                id_ps_dialog_turn=dialog_turn_id,
                id_dataset=dataset_id,
            )
            db.session.add(dialog_turn_annotation)
    elif speaker == Speaker.therapist:
        for dialog_turn_id in dialog_turn_ids:
            dialog_turn_annotation = PSDialogTurnAnnotation(
                label_a_therapist=form.label_a_therapist.data,
                label_b_therapist=form.label_b_therapist.data,
                label_c_therapist=form.label_c_therapist.data,
                label_d=form.label_d.data,
                label_e=form.label_e.data,
                strength_a=form.strength_a.data,
                strength_b=form.strength_b.data,
                strength_c=form.strength_c.data,
                strength_d=form.strength_d.data,
                strength_e=form.strength_e.data,
                comment_a=form.comment_a.data,
                comment_b=form.comment_b.data,
                comment_c=form.comment_c.data,
                comment_d=form.comment_d.data,
                comment_e=form.comment_e.data,
                speaker=speaker,
                id_user=current_user.id,
                id_ps_dialog_turn=dialog_turn_id,
                id_dataset=dataset_id,
            )
            db.session.add(dialog_turn_annotation)
