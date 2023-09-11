from app.annotate import bp
from app import db
from flask import render_template, request, url_for, current_app, abort, flash, redirect
from flask_login import login_required
from app.models import Dataset
from app.utils import Speaker
from app.annotate.utils import (
    split_dialog_turns,
    get_events_from_segments,
    get_page_items,
    fetch_dialog_turn_annotations,
    new_dialog_turn_annotation_to_db,
    create_psy_annotation_forms,
)


@bp.route("/annotate_psychotherapy/<int:dataset_id>", methods=["GET", "POST"])
@login_required
def annotate_ps(dataset_id):
    """This is the annotations page for psychotherapy datasets"""
    dataset = Dataset.query.get_or_404(
        dataset_id
    )  # fetch the dataset from the database
    dialog_turns = dataset.dialog_turns.order_by(
        "timestamp"
    ).all()  # fetch all dialog turns associated with the dataset
    try:
        # split the dialog turns into segments of a given time interval (specified in the app config)
        app_config = current_app.config  # Get the app config
        segments = split_dialog_turns(
            dialog_turns, time_interval=app_config["PS_MINS_PER_PAGE"] * 60
        )
        # get the events corresponding to each segment
        events = get_events_from_segments(segments)  # a list of lists containing events
        # get the page number from the request
        page = request.args.get("page", 1, type=int)  # default page is 1
        # get the events for the current page and the urls for the pager
        (
            page_items,
            next_url,
            prev_url,
            first_url,
            last_url,
            total_pages,
        ) = get_page_items(page, events, dataset_id)
        start_times = [
            segment[0].timestamp for segment in segments
        ]  # the starting times of each segment
        start_time = start_times[page - 1]  # get the starting time of the current page
        # get the IDs of the dialog turns in the current page
        dialog_turn_ids = [dialog_turn.id for dialog_turn in segments[page - 1]]
        # fetch the annotations for the current page
        annotations_client = fetch_dialog_turn_annotations(
            dialog_turns=segments[page - 1], speaker=Speaker.client
        )
        annotations_therapist = fetch_dialog_turn_annotations(
            dialog_turns=segments[page - 1], speaker=Speaker.therapist
        )
        annotations_dyad = fetch_dialog_turn_annotations(
            dialog_turns=segments[page - 1], speaker=Speaker.dyad
        )
        # create the forms
        [form_client, form_therapist, form_dyad] = create_psy_annotation_forms(
            annotations_client, annotations_therapist, annotations_dyad
        )
        # the submit button is named "submit_form_client", "submit_form_therapist" or
        # "submit_form_dyad" depending on the speaker
        if "submit_form_client" in request.form:
            # the condition below checks that the form was submitted (via POST request) and that all validators pass
            if form_client.validate_on_submit():
                speaker = Speaker.client
                # add the annotations to the database session
                try:
                    new_dialog_turn_annotation_to_db(
                        form_client, speaker, dataset_id, dialog_turn_ids
                    )
                except:
                    db.session.rollback()
                    abort(500)
                # commit the changes to the database
                db.session.commit()
                flash("Your annotations have been saved.", "success")
                return redirect(
                    url_for("annotate.annotate_ps", dataset_id=dataset_id, page=page)
                )  # redirect to the same page
        elif "submit_form_therapist" in request.form:
            # the condition below checks that the form was submitted (via POST request) and that all validators pass
            if form_therapist.validate_on_submit():
                speaker = Speaker.therapist
                # add the annotations to the database session
                try:
                    new_dialog_turn_annotation_to_db(
                        form_therapist, speaker, dataset_id, dialog_turn_ids
                    )
                except:
                    db.session.rollback()
                    abort(500)
                # commit the changes to the database
                db.session.commit()
                flash("Your annotations have been saved.", "success")
                return redirect(
                    url_for("annotate.annotate_ps", dataset_id=dataset_id, page=page)
                )  # redirect to the same page
        elif "submit_form_dyad" in request.form:
            # the condition below checks that the form was submitted (via POST request) and that all validators pass
            if form_dyad.validate_on_submit():
                speaker = Speaker.dyad
                # add the annotations to the database session
                try:
                    new_dialog_turn_annotation_to_db(
                        form_dyad, speaker, dataset_id, dialog_turn_ids
                    )
                except:
                    db.session.rollback()
                    abort(500)
                # commit the changes to the database
                db.session.commit()
                flash("Your annotations have been saved.", "success")
                return redirect(
                    url_for("annotate.annotate_ps", dataset_id=dataset_id, page=page)
                )
        return render_template(
            "annotate/annotate_ps.html",
            dataset_name=dataset.name,
            page_items=page_items,
            next_url=next_url,
            prev_url=prev_url,
            first_url=first_url,
            last_url=last_url,
            start_time=start_time,
            page=page,
            total_pages=total_pages,
            form_client=form_client,
            form_therapist=form_therapist,
            form_dyad=form_dyad,
            annotations_client=annotations_client,
            annotations_therapist=annotations_therapist,
            annotations_dyad=annotations_dyad,
        )
    except IndexError:
        # if there are no dialog turns in the dataset, return the template without any events
        return render_template("annotate/annotate_ps.html", dataset_name=dataset.name)


@bp.route("/annotate_social_media/<int:dataset_id>")
@login_required
def annotate_sm(dataset_id):
    """This is the annotations page for social media datasets"""
    dataset = Dataset.query.get_or_404(
        dataset_id
    )  # fetch the dataset from the database
    return render_template("annotate/annotate_sm.html", dataset=dataset)
