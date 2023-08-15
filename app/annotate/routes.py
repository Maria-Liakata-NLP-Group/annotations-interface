from app.annotate import bp
from app.annotate.forms import PSAnnotationFormClient, PSAnnotationFormTherapist
from app import db
from flask import render_template, request, url_for, current_app, abort, flash, redirect
from flask_login import login_required, current_user
from app.models import Dataset, PSDialogTurnAnnotation
from app.utils import Speaker
from app.annotate.utils import (
    split_dialog_turns,
    get_events_from_sections,
    get_page_items,
)


def new_dialog_turn_annotation_to_db(form, speaker, dataset_id, dialog_turn_ids):
    """
    Create a new psychotherapy dialog turn annotation object and add it to the database session.
    Loops through the dialog turn IDs and creates a new annotation for each one.
    """
    for dialog_turn_id in dialog_turn_ids:
        dialog_turn_annotation = PSDialogTurnAnnotation(
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
            speaker=speaker,
            id_user=current_user.id,
            id_ps_dialog_turn=dialog_turn_id,
            id_dataset=dataset_id,
        )
        db.session.add(dialog_turn_annotation)


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
        # split the dialog turns into sections of a given time interval (specified in the app config)
        app_config = current_app.config  # Get the app config
        sections = split_dialog_turns(
            dialog_turns, time_interval=app_config["PS_MINS_PER_PAGE"] * 60
        )
        # get the events corresponding to each section
        events = get_events_from_sections(sections)  # a list of lists containing events
        # get the page number from the request
        page = request.args.get("page", 1, type=int)  # default page is 1
        (
            page_items,
            next_url,
            prev_url,
            first_url,
            last_url,
            total_pages,
        ) = get_page_items(
            page, events, dataset_id
        )  # get the events for the current page and the urls for the pager
        start_times = [
            section[0].timestamp for section in sections
        ]  # the starting times of each section
        start_time = start_times[page - 1]  # get the starting time of the current page
        # get the IDs of the dialog turns in the current page
        dialog_turn_ids = [dialog_turn.id for dialog_turn in sections[page - 1]]
        # create annotation form instances for the client and the therapist
        form_client = PSAnnotationFormClient()
        form_therapist = PSAnnotationFormTherapist()
        # the submit button is named "submit_form_client" or "submit_form_therapist" depending on the speaker
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
        )
    except IndexError:
        # if there are no dialog turns in the dataset, return the template without any events
        return render_template("annotate/annotate_ps.html", dataset_name=dataset.name)


@bp.route("/annotate_sm/<int:dataset_id>")
@login_required
def annotate_sm(dataset_id):
    """This is the annotations page for social media datasets"""
    dataset = Dataset.query.get_or_404(
        dataset_id
    )  # fetch the dataset from the database
    return render_template("annotate/annotate_sm.html", dataset=dataset)
