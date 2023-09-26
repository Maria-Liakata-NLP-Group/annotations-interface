"""
Miscellaneous utility functions for the annotate blueprint
"""
from flask_wtf import FlaskForm
from datetime import datetime
import itertools
from flask import url_for
from flask_login import current_user
from app.utils import Speaker
from sqlalchemy import desc
from app.models import (
    PSAnnotationClient,
    PSDialogTurnAnnotationTherapist,
    PSDialogTurnAnnotationDyad,
)
from app import db
from app.annotate.forms import (
    PSAnnotationFormClient,
    PSAnnotationFormTherapist,
    PSAnnotationFormDyad,
)


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
    Fetch the annotations for the dialog turns from the database and
    only return the annotation with the latest timestamp.

    Parameters
    ----------
    dialog_turns : list
        A list of PSDialogTurn objects
    speaker : Speaker
        The speaker the annotation is for (client, therapist or dyad)

    Returns
    -------
    annotation : PSAnnotationClient or PSDialogTurnAnnotationTherapist or PSDialogTurnAnnotationDyad or None
        The annotation with the latest timestamp for the client, therapist or dyad if it exists, otherwise None.
        The "label_*" and "strength_*" attributes are converted to their corresponding Enum values.
    """

    annotations = []
    if speaker == Speaker.client:
        for dialog_turn in dialog_turns:
            annotation = (
                dialog_turn.annotations_client.filter_by(id_user=current_user.id)
                .order_by(desc("timestamp"))
                .first()
            )  # for this dialog turn, get the annotation for the client with the latest timestamp
            if annotation:
                annotations.append(annotation)
    elif speaker == Speaker.therapist:
        for dialog_turn in dialog_turns:
            annotation = (
                dialog_turn.annotations_therapist.filter_by(id_user=current_user.id)
                .order_by(desc("timestamp"))
                .first()
            )  # for this dialog turn, get the annotation for the therapist with the latest timestamp
            if annotation:
                annotations.append(annotation)
    elif speaker == Speaker.dyad:
        for dialog_turn in dialog_turns:
            annotation = (
                dialog_turn.annotations_dyad.filter_by(id_user=current_user.id)
                .order_by(desc("timestamp"))
                .first()
            )  # for this dialog turn, get the annotation for the dyad with the latest timestamp
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
            elif attr.startswith("strength_") and getattr(annotation, attr) is not None:
                setattr(annotation, attr, getattr(annotation, attr).name)
    else:
        annotation = None
    return annotation


def new_dialog_turn_annotation_to_db(form, speaker, dataset_id, dialog_turns):
    """
    Create a new psychotherapy dialog turn annotation object and add it to the database session.

    Parameters
    ----------
    form : PSAnnotationFormClient or PSAnnotationFormTherapist or PSAnnotationFormDyad
        The form containing the annotation data
    speaker : Speaker
        The speaker the annotation is for (client, therapist or dyad)
    dataset_id : int
        The id of the dataset the dialog turns belong to
    dialog_turns : list of PSDialogTurn objects
        The dialog turns the annotation is for
    """
    if speaker == Speaker.client:
        dialog_turn_annotation = PSAnnotationClient(
            label_a=form.label_a.data,
            label_b=form.label_b.data,
            label_c=form.label_c.data,
            label_d=form.label_d.data,
            label_e=form.label_e.data,
            label_f=form.label_f.data,
            strength_a=form.strength_a.data,
            strength_b=form.strength_b.data,
            strength_c=form.strength_c.data,
            strength_d=form.strength_d.data,
            strength_e=form.strength_e.data,
            strength_f=form.strength_f.data,
            comment_a=form.comment_a.data,
            comment_b=form.comment_b.data,
            comment_c=form.comment_c.data,
            comment_d=form.comment_d.data,
            comment_e=form.comment_e.data,
            comment_f=form.comment_f.data,
            comment_summary=form.comment_summary.data,
            id_user=current_user.id,
            id_dataset=dataset_id,
        )
    elif speaker == Speaker.therapist:
        dialog_turn_annotation = PSDialogTurnAnnotationTherapist(
            label_a=form.label_a.data,
            label_b=form.label_b.data,
            label_c=form.label_c.data,
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
            comment_summary=form.comment_summary.data,
            id_user=current_user.id,
            id_dataset=dataset_id,
        )
    elif speaker == Speaker.dyad:
        dialog_turn_annotation = PSDialogTurnAnnotationDyad(
            label_a=form.label_a.data,
            label_b=form.label_b.data,
            strength_a=form.strength_a.data,
            strength_b=form.strength_b.data,
            comment_a=form.comment_a.data,
            comment_b=form.comment_b.data,
            comment_summary=form.comment_summary.data,
            id_user=current_user.id,
            id_dataset=dataset_id,
        )
    for dialog_turn in dialog_turns:
        dialog_turn_annotation.dialog_turns.append(dialog_turn)
    db.session.add(dialog_turn_annotation)


def create_psy_annotation_forms(
    annotations_client, annotations_therapist, annotations_dyad
):
    """
    Create the annotation forms for the psychotherapy dialog turns,
    either pre-populated with previous annotation values or empty.

    Parameters
    ----------
    annotations_client : PSAnnotationClient or None for client annotations
    annotations_therapist : PSDialogTurnAnnotationTherapist or None for therapist annotations
    annotations_dyad : PSDialogTurnAnnotationDyad or None for dyad annotations

    Returns
    -------
    form_client : PSAnnotationFormClient (pre-populated with previous annotation values or empty)
    form_therapist : PSAnnotationFormTherapist (pre-populated with previous annotation values or empty)
    form_dyad : PSAnnotationFormDyad (pre-populated with previous annotation values or empty)
    """

    if annotations_client:
        # if there are annotations, fill the form with the values
        form_client = PSAnnotationFormClient(obj=annotations_client)
    else:
        # if there are no annotations, create an empty form
        form_client = PSAnnotationFormClient()
    if annotations_therapist:
        form_therapist = PSAnnotationFormTherapist(obj=annotations_therapist)
    else:
        form_therapist = PSAnnotationFormTherapist()
    if annotations_dyad:
        form_dyad = PSAnnotationFormDyad(obj=annotations_dyad)
    else:
        form_dyad = PSAnnotationFormDyad()
    return form_client, form_therapist, form_dyad


def get_dynamic_choices(page_items: list, speaker: Speaker):
    """
    Get the dynamic choices for the select multiple field in the annotation form.

    Parameters
    ----------
    page_items : list of PSDialogEvent objects
        The events for the current page
    speaker : Speaker
        The speaker the annotation is for (client, therapist or dyad)

    Returns
    -------
    choices : list of tuples
        A list of tuples containing the event IDs and event numbers, to be used as choices
        for the select multiple field
    """

    if speaker == Speaker.client:
        choices = [
            (item.id, item.event_n)
            for item in page_items
            if item.event_speaker.lower() == "client"
        ]
    elif speaker == Speaker.therapist:
        choices = [
            (item.id, item.event_n)
            for item in page_items
            if item.event_speaker.lower() == "therapist"
        ]
    elif speaker == Speaker.dyad:
        choices = [
            (item.id, item.event_n) for item in page_items
        ]  # all events are shown for the dyad
    return choices


def assign_dynamic_choices(form: FlaskForm, page_items: list, speaker: Speaker):
    """
    Assign the dynamic choices to the select fields or select multiple fields in the annotation form.

    Parameters
    ----------
    form : PSAnnotationFormClient or PSAnnotationFormTherapist or PSAnnotationFormDyad
        The annotation form
    page_items : list of PSDialogEvent objects
        The events for the current page
    speaker : Speaker
        The speaker the annotation is for (client, therapist or dyad)

    Returns
    -------
    form : PSAnnotationFormClient or PSAnnotationFormTherapist or PSAnnotationFormDyad
        The annotation form with the dynamic choices assigned to the select fields or select
        multiple fields that start with "start_event_", "end_event_" or "relevant_events_"
    """

    choices = get_dynamic_choices(page_items, speaker)
    # find the select multiple field(s) in the form. They all start with "relevant_events_".
    for field_name in form.__dict__.keys():
        if (
            field_name.startswith("relevant_events_")
            or field_name.startswith("start_event_")
            or field_name.startswith("end_event_")
        ):
            form[field_name].choices = choices
    return form
