"""
Miscellaneous utility functions for the annotate blueprint
"""
from typing import Union
from datetime import datetime
import itertools
from flask import url_for, abort
from flask_login import current_user
from app.utils import Speaker, LabelNamesClient, LabelNamesTherapist, LabelNamesDyad
from sqlalchemy import desc
from app.models import (
    PSAnnotationClient,
    PSAnnotationTherapist,
    PSAnnotationDyad,
    EvidenceClient,
    EvidenceTherapist,
    EvidenceDyad,
    Dataset,
    ClientAnnotationSchema,
    TherapistAnnotationSchema,
    DyadAnnotationSchema,
    ClientAnnotationSchemaAssociation,
    ClientAnnotationComment,
)
from app import db
from app.annotate.forms import (
    PSAnnotationFormClient,
    PSAnnotationFormTherapist,
    PSAnnotationFormDyad,
)


def split_dialog_turns(dialog_turns: list, time_interval: int = 300) -> list:
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


def get_events_from_segments(segments: list) -> list:
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


def get_page_items(page: int, events: list, dataset_id: int):
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


def fetch_dialog_turn_annotations(
    dialog_turns: list, speaker: Speaker
) -> Union[None, PSAnnotationClient, PSAnnotationTherapist, PSAnnotationDyad]:
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
    annotation : PSAnnotationClient or PSAnnotationTherapist or PSAnnotationDyad or None
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


def new_dialog_turn_annotation_to_db(
    form: Union[
        PSAnnotationFormClient, PSAnnotationFormTherapist, PSAnnotationFormDyad
    ],
    speaker: Speaker,
    dataset: Dataset,
    dialog_turns: list,
):
    """
    Create a new psychotherapy dialog turn annotation object and add it to the database session.

    Parameters
    ----------
    form : PSAnnotationFormClient or PSAnnotationFormTherapist or PSAnnotationFormDyad
        The form containing the annotation data
    speaker : Speaker
        The speaker the annotation is for (client, therapist or dyad)
    dataset : Dataset
        The dataset object the annotation is for
    dialog_turns : list of PSDialogTurn objects
        The dialog turns the annotation is for
    """

    # create the annotation object for the client, therapist or dyad
    if speaker == Speaker.client:
        annotation_model = PSAnnotationClient
        association_model = ClientAnnotationSchemaAssociation
        annotation_schema = ClientAnnotationSchema()
        evidence_model = EvidenceClient
    elif speaker == Speaker.therapist:
        annotation_model = PSAnnotationTherapist
        annotation_schema = TherapistAnnotationSchema()
    elif speaker == Speaker.dyad:
        annotation_model = PSAnnotationDyad
        annotation_schema = DyadAnnotationSchema()

    annotation = annotation_model(
        comment_summary=form.comment_summary.data,
        author=current_user,
        dataset=dataset,
    )
    db.session.add(annotation)

    # add the dialog turns to the annotation
    for dialog_turn in dialog_turns:
        annotation.dialog_turns.append(dialog_turn)

    # find all the `name_*` attributes in the form (i.e. name_a, name_b, name_c, etc.)
    # these are the parent labels in the annotation schema
    names = [attr for attr in dir(form) if attr.startswith("name_")]
    for name in names:
        parent_label = annotation_schema.query.filter_by(
            label=getattr(form, name)
        ).first()
        if parent_label is None:
            print(f"Parent label {getattr(form, name).data} not found in the database")
            abort(404)
        letter = name.split("_")[1]  # i.e. a, b, c, etc.
        # find all the attributes in the form that end with "_letter"
        attrs = [attr for attr in form.__dict__.keys() if attr.endswith("_" + letter)]
        # split these into main and additional (contain "_add_") attributes
        main_attrs = [attr for attr in attrs if "_add_" not in attr]
        add_attrs = [attr for attr in attrs if "_add_" in attr]

        # deal with main attributes first
        # labels and sub labels
        attrs = [
            attr
            for attr in main_attrs
            if all(
                [
                    attr.startswith("label_") or attr.startswith("sublabel_"),
                    getattr(form, attr).data != 0,
                ]
            )
        ]
        label_ids = [getattr(form, attr).data for attr in attrs]
        new_labels_to_db(label_ids, annotation, annotation_schema, association_model)
        # add the main comments to the annotation
        attrs = [
            attr
            for attr in main_attrs
            if attr.startswith("comment_") and getattr(form, attr).data
        ]
        comments = [getattr(form, attr).data for attr in attrs]
        new_comments_to_db(comments, annotation, parent_label)

        # now deal with the additional attributes
        # labels and sub labels
        attrs = [
            attr
            for attr in add_attrs
            if all(
                [
                    attr.startswith("label_") or attr.startswith("sublabel_"),
                    getattr(form, attr).data != 0,
                ]
            )
        ]
        label_ids = [getattr(form, attr).data for attr in attrs]
        new_labels_to_db(
            label_ids, annotation, annotation_schema, association_model, additional=True
        )
        # comments
        attrs = [
            attr
            for attr in add_attrs
            if attr.startswith("comment_") and getattr(form, attr).data
        ]
        comments = [getattr(form, attr).data for attr in attrs]
        new_comments_to_db(comments, annotation, parent_label, additional=True)

    # new_client_evidence_events_to_db(form, annotation)
    # new_therapist_evidence_events_to_db(form, annotation)
    # new_dyad_evidence_events_to_db(form, annotation)


def new_labels_to_db(
    label_ids: list,
    annotation: Union[PSAnnotationClient, PSAnnotationTherapist, PSAnnotationDyad],
    annotation_schema: Union[
        ClientAnnotationSchema, TherapistAnnotationSchema, DyadAnnotationSchema
    ],
    association_model: ClientAnnotationSchemaAssociation,
    additional: bool = False,
):
    for id in label_ids:
        label = annotation_schema.query.get_or_404(id)
        if additional:
            association = association_model(
                label=label,
                annotation=annotation,
                is_additional=True,
            )
            db.session.add(association)
        else:
            annotation.annotation_labels.append(label)


def new_comments_to_db(
    comments: list,
    annotation: Union[PSAnnotationClient, PSAnnotationTherapist, PSAnnotationDyad],
    parent_label: ClientAnnotationSchema,
    additional: bool = False,
):
    for comment in comments:
        comment_obj = ClientAnnotationComment(
            comment=comment,
            is_additional=additional,
        )
        db.session.add(comment_obj)
        annotation.annotation_comments.append(comment_obj)
        parent_label.comments.append(comment_obj)


def new_client_evidence_events_to_db(
    form: PSAnnotationFormClient, annotation: PSAnnotationClient
):
    """
    Given a new annotation for the client, add the evidence
    events of the form to the database session.
    """

    events_a = form.relevant_events_a.data  # these are events IDs
    events_b = form.relevant_events_b.data
    events_c = form.relevant_events_c.data
    events_d = form.relevant_events_d.data
    events_e = form.relevant_events_e.data
    start_event_f = form.startevent_f.data
    end_event_f = form.endevent_f.data

    evidences = []
    for event in events_a:
        evidence = EvidenceClient(
            annotation=annotation,
            id_ps_dialog_event=event,
            label=LabelNamesClient.label_a,
        )
        evidences.append(evidence)
    for event in events_b:
        evidence = EvidenceClient(
            annotation=annotation,
            id_ps_dialog_event=event,
            label=LabelNamesClient.label_b,
        )
        evidences.append(evidence)
    for event in events_c:
        evidence = EvidenceClient(
            annotation=annotation,
            id_ps_dialog_event=event,
            label=LabelNamesClient.label_c,
        )
        evidences.append(evidence)
    for event in events_d:
        evidence = EvidenceClient(
            annotation=annotation,
            id_ps_dialog_event=event,
            label=LabelNamesClient.label_d,
        )
        evidences.append(evidence)
    for event in events_e:
        evidence = EvidenceClient(
            annotation=annotation,
            id_ps_dialog_event=event,
            label=LabelNamesClient.label_e,
        )
        evidences.append(evidence)
    if start_event_f and end_event_f:
        for event in range(start_event_f, end_event_f + 1):
            evidence = EvidenceClient(
                annotation=annotation,
                id_ps_dialog_event=event,
                label=LabelNamesClient.label_f,
            )
            evidences.append(evidence)
    db.session.add_all(evidences)


def new_therapist_evidence_events_to_db(
    form: PSAnnotationFormTherapist, annotation: PSAnnotationTherapist
):
    """
    Given a new annotation for the therapist, add the evidence
    events of the form to the database session.
    """

    events_a = form.relevant_events_a.data  # these are events IDs
    events_b = form.relevant_events_b.data
    events_c = form.relevant_events_c.data
    events_d = form.relevant_events_d.data
    events_e = form.relevant_events_e.data

    evidences = []
    for event in events_a:
        evidence = EvidenceTherapist(
            annotation=annotation,
            id_ps_dialog_event=event,
            label=LabelNamesTherapist.label_a,
        )
        evidences.append(evidence)
    for event in events_b:
        evidence = EvidenceTherapist(
            annotation=annotation,
            id_ps_dialog_event=event,
            label=LabelNamesTherapist.label_b,
        )
        evidences.append(evidence)
    for event in events_c:
        evidence = EvidenceTherapist(
            annotation=annotation,
            id_ps_dialog_event=event,
            label=LabelNamesTherapist.label_c,
        )
        evidences.append(evidence)
    for event in events_d:
        evidence = EvidenceTherapist(
            annotation=annotation,
            id_ps_dialog_event=event,
            label=LabelNamesTherapist.label_d,
        )
        evidences.append(evidence)
    for event in events_e:
        evidence = EvidenceTherapist(
            annotation=annotation,
            id_ps_dialog_event=event,
            label=LabelNamesTherapist.label_e,
        )
        evidences.append(evidence)
    db.session.add_all(evidences)


def new_dyad_evidence_events_to_db(
    form: PSAnnotationFormDyad, annotation: PSAnnotationDyad
):
    """
    Given a new annotation for the dyad, add the evidence
    events of the form to the database session.
    """

    events_a = form.relevant_events_a.data  # these are events IDs
    events_b = form.relevant_events_b.data

    evidences = []
    for event in events_a:
        evidence = EvidenceDyad(
            annotation=annotation,
            id_ps_dialog_event=event,
            label=LabelNamesDyad.label_a,
        )
        evidences.append(evidence)
    for event in events_b:
        evidence = EvidenceDyad(
            annotation=annotation,
            id_ps_dialog_event=event,
            label=LabelNamesDyad.label_b,
        )
        evidences.append(evidence)
    db.session.add_all(evidences)


def create_psy_annotation_form(
    annotations: Union[
        PSAnnotationClient, PSAnnotationTherapist, PSAnnotationDyad, None
    ],
    speaker: Speaker,
) -> Union[PSAnnotationFormClient, PSAnnotationFormTherapist, PSAnnotationFormDyad]:
    """
    Create the annotation form for the psychotherapy dialog turns,
    either pre-populated with previous annotation values or empty.

    Parameters
    ----------
    annotations : PSAnnotationClient or PSAnnotationTherapist or PSAnnotationDyad or None
        The annotations object for the client, therapist or dyad if it exists, otherwise None
    speaker : Speaker
        The speaker the annotation is for (client, therapist or dyad)

    Returns
    -------
    form : PSAnnotationFormClient or PSAnnotationFormTherapist or PSAnnotationFormDyad
        The annotation form, either pre-populated with previous annotation values or empty (if there are no annotations)
    """

    if speaker == Speaker.client:
        if annotations:
            # for the time being skip the block below
            # TODO: need to fix the function fetch_evidence_client() first
            form = PSAnnotationFormClient()
            return form
            # if there are annotations, fill the form with the values
            (
                id_events_a,
                id_events_b,
                id_events_c,
                id_events_d,
                id_events_e,
                id_start_event_f,
                id_end_event_f,
            ) = fetch_evidence_client(annotations)
            form = PSAnnotationFormClient(
                obj=annotations,
                relevant_events_a=id_events_a,
                relevant_events_b=id_events_b,
                relevant_events_c=id_events_c,
                relevant_events_d=id_events_d,
                relevant_events_e=id_events_e,
                start_event_f=id_start_event_f,
                end_event_f=id_end_event_f,
            )
        else:
            # if there are no annotations, create an empty form
            form = PSAnnotationFormClient()
    elif speaker == Speaker.therapist:
        if annotations:
            # for the time being skip the block below
            # TODO: need to fix the function fetch_evidence_therapist() first
            form = PSAnnotationFormTherapist()
            return form
            # if there are annotations, fill the form with the values
            (
                id_events_a,
                id_events_b,
                id_events_c,
                id_events_d,
                id_events_e,
            ) = fetch_evidence_therapist(annotations)
            form = PSAnnotationFormTherapist(
                obj=annotations,
                relevant_events_a=id_events_a,
                relevant_events_b=id_events_b,
                relevant_events_c=id_events_c,
                relevant_events_d=id_events_d,
                relevant_events_e=id_events_e,
            )
        else:
            # if there are no annotations, create an empty form
            form = PSAnnotationFormTherapist()
    elif speaker == Speaker.dyad:
        if annotations:
            # for the time being skip the block below
            # TODO: need to fix the function fetch_evidence_dyad() first
            form = PSAnnotationFormDyad()
            return form
            # if there are annotations, fill the form with the values
            (id_events_a, id_events_b) = fetch_evidence_dyad(annotations)
            form = PSAnnotationFormDyad(
                obj=annotations,
                relevant_events_a=id_events_a,
                relevant_events_b=id_events_b,
            )
        else:
            # if there are no annotations, create an empty form
            form = PSAnnotationFormDyad()
    return form


def get_evidence_dynamic_choices(page_items: list, speaker: Speaker) -> list:
    """
    Get the dynamic choices for the evidence select fields in the annotation form.
    This is used to populate the select fields with the events for the current page,
    to be used as evidence for the annotation.

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
        for the evidence select fields
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


def assign_dynamic_choices(
    form: Union[
        PSAnnotationFormClient, PSAnnotationFormTherapist, PSAnnotationFormDyad
    ],
    page_items: list,
    speaker: Speaker,
) -> Union[PSAnnotationFormClient, PSAnnotationFormTherapist, PSAnnotationFormDyad]:
    """
    Assign the dynamic choices to the select fields or select multiple fields in the
    annotation form. Specifically to the labels, scales and evidence fields. For the
    sub labels, assign a placeholder of value 0 with no label. An AJAX call is made
    to the server later to get the actual choices dynamically.

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
        multiple fields that start with "label_", "scale_", "startevent_", "endevent_" or
        "evidence_". For the sub labels, assign a placeholder of value 0 with no label. An
        AJAX call is made to the server later to get the actual choices dynamically.
    """

    # assign the dynamic choices to the select fields or select multiple fields
    # that start with "startevent_", "endevent_" or "evidence_"
    choices = get_evidence_dynamic_choices(page_items, speaker)
    for field_name in form.__dict__.keys():
        if (
            field_name.startswith("evidence_")
            or field_name.startswith("startevent_")
            or field_name.startswith("endevent_")
        ):
            form[field_name].choices = choices

    # find all the form group names in the form (i.e. name_a, name_b, name_c, etc.)
    # assign the corresponding choices to their respective labels (i.e. label_a, label_b, label_c, etc.)
    # and scales (i.e. scale_(i)_a, scale_(i)_b, scale_(i)_c, etc.)
    if speaker == Speaker.client:
        annotation_schema = ClientAnnotationSchema()
    elif speaker == Speaker.therapist:
        annotation_schema = TherapistAnnotationSchema()
    elif speaker == Speaker.dyad:
        annotation_schema = DyadAnnotationSchema()
    names = [attr for attr in dir(form) if attr.startswith("name_")]
    scales = [attr for attr in dir(form) if attr.startswith("scale_")]

    for name in names:
        parent_label = getattr(form, name)
        choices = annotation_schema.get_label_children(parent_label)
        letter = name.split("_")[1]  # i.e. a, b, c, etc.
        label_attr = "label_" + letter  # i.e. label_a, label_b, label_c, etc.
        label_attr_add = (
            "label" + "_add_" + letter
        )  # i.e. label_add_a, label_add_b, label_add_c, etc.
        if label_attr in form.__dict__.keys():
            form[label_attr].choices = choices
        if label_attr_add in form.__dict__.keys():
            form[label_attr_add].choices = choices
        for scale in scales:
            if scale.endswith("_" + letter):
                scale_title = getattr(form, scale).label.text
                choices = annotation_schema.get_label_scales(parent_label, scale_title)
                form[scale].choices = choices

    # find all the sub label names in the form and assign a placeholder of value 0 with no label
    # an AJAX call is made to the server later to get the actual choices dynamically
    sub_labels = [attr for attr in dir(form) if attr.startswith("sublabel_")]
    for sub_label in sub_labels:
        form[sub_label].choices = [(0, "")]

    return form


def fetch_evidence_client(annotation: PSAnnotationClient):
    """
    Given a client annotation, fetch the evidence events from the database
    and return them as a list of event IDs.

    Parameters
    ----------
    annotation : PSAnnotationClient
        The annotation object for the client

    Returns
    -------
    Lists of event IDs for the evidence events for each label and the start
    and end event IDs for label F
    """

    evidence = annotation.evidence

    label_names = [
        LabelNamesClient.label_a,
        LabelNamesClient.label_b,
        LabelNamesClient.label_c,
        LabelNamesClient.label_d,
        LabelNamesClient.label_e,
    ]

    events = {}
    for label in label_names:
        filtered_events = evidence.filter_by(label=label).all()
        if filtered_events:
            events[label] = [event.id_ps_dialog_event for event in filtered_events]
        else:
            events[label] = []

    ordered_events_f = (
        evidence.filter_by(label=LabelNamesClient.label_f)
        .order_by("id_ps_dialog_event")
        .all()
    )

    id_start_event_f = (
        ordered_events_f[0].id_ps_dialog_event if ordered_events_f else None
    )
    id_end_event_f = (
        ordered_events_f[-1].id_ps_dialog_event if ordered_events_f else None
    )

    return (
        events[LabelNamesClient.label_a],
        events[LabelNamesClient.label_b],
        events[LabelNamesClient.label_c],
        events[LabelNamesClient.label_d],
        events[LabelNamesClient.label_e],
        id_start_event_f,
        id_end_event_f,
    )


def fetch_evidence_therapist(annotation: PSAnnotationTherapist):
    """
    Given a therapist annotation, fetch the evidence events from the database
    and return them as a list of event IDs.

    Parameters
    ----------
    annotation : PSAnnotationTherapist
        The annotation object for the therapist

    Returns
    -------
    Lists of event IDs for the evidence events for each label
    """

    evidence = annotation.evidence

    label_names = [
        LabelNamesTherapist.label_a,
        LabelNamesTherapist.label_b,
        LabelNamesTherapist.label_c,
        LabelNamesTherapist.label_d,
        LabelNamesTherapist.label_e,
    ]

    events = {}
    for label in label_names:
        filtered_events = evidence.filter_by(label=label).all()
        if filtered_events:
            events[label] = [event.id_ps_dialog_event for event in filtered_events]
        else:
            events[label] = []

    return (
        events[LabelNamesTherapist.label_a],
        events[LabelNamesTherapist.label_b],
        events[LabelNamesTherapist.label_c],
        events[LabelNamesTherapist.label_d],
        events[LabelNamesTherapist.label_e],
    )


def fetch_evidence_dyad(annotation: PSAnnotationDyad):
    """
    Given a dyad annotation, fetch the evidence events from the database
    and return them as a list of event IDs.

    Parameters
    ----------
    annotation : PSAnnotationDyad
        The annotation object for the dyad

    Returns
    -------
    Lists of event IDs for the evidence events for each label
    """

    evidence = annotation.evidence

    label_names = [
        LabelNamesDyad.label_a,
        LabelNamesDyad.label_b,
    ]

    events = {}
    for label in label_names:
        filtered_events = evidence.filter_by(label=label).all()
        if filtered_events:
            events[label] = [event.id_ps_dialog_event for event in filtered_events]
        else:
            events[label] = []

    return (
        events[LabelNamesDyad.label_a],
        events[LabelNamesDyad.label_b],
    )
