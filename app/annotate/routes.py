from app.annotate import bp
from app import db
from flask import render_template, request, url_for, current_app, abort, flash, redirect
from flask.views import View
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
    assign_dynamic_choices,
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
            annotations_client,
            annotations_therapist,
            annotations_dyad,
        )
        form_client = assign_dynamic_choices(form_client, page_items, Speaker.client)
        form_therapist = assign_dynamic_choices(
            form_therapist, page_items, Speaker.therapist
        )
        form_dyad = assign_dynamic_choices(form_dyad, page_items, Speaker.dyad)
        # the submit button is named "submit_form_client", "submit_form_therapist" or
        # "submit_form_dyad" depending on the speaker
        if "submit_form_client" in request.form:
            # the condition below checks that the form was submitted (via POST request) and that all validators pass
            if form_client.validate_on_submit():
                speaker = Speaker.client
                # add the annotations to the database session
                try:
                    new_dialog_turn_annotation_to_db(
                        form_client,
                        speaker,
                        dataset,
                        dialog_turns=segments[page - 1],
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
                        form_therapist,
                        speaker,
                        dataset,
                        dialog_turns=segments[page - 1],
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
                        form_dyad, speaker, dataset, dialog_turns=segments[page - 1]
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


# rewrite the view function above as a reusable class-based view
class AnnotatePsy(View):
    def __init__(self, speaker, dataset_id):
        self.speaker = speaker
        self.dataset = Dataset.query.get_or_404(dataset_id)
        self.template = f"annotate/{speaker.name}.html"

    def get_items_for_this_page(self, page, segments):
        start_times = [segment[0].timestamp for segment in segments]
        start_time = start_times[page - 1]  # get the starting time of the current page
        events = get_events_from_segments(segments)
        (
            page_items,
            next_url,
            prev_url,
            first_url,
            last_url,
            total_pages,
        ) = get_page_items(
            page, events, self.dataset.id
        )  # get the events for the current page and the urls for the pager
        return (
            page_items,
            next_url,
            prev_url,
            first_url,
            last_url,
            total_pages,
            start_time,
        )

    def create_form(self, dialog_turns, page_items):
        annotations = fetch_dialog_turn_annotations(
            dialog_turns=dialog_turns, speaker=self.speaker
        )
        form = create_psy_annotation_forms(annotations)
        form = assign_dynamic_choices(form, page_items, self.speaker)
        return form

    def dispatch_request(self, dataset_id):
        app_config = current_app.config
        segments = split_dialog_turns(
            self.dataset.dialog_turns.order_by("timestamp").all(),
            time_interval=app_config["PS_MINS_PER_PAGE"] * 60,
        )  # split the dialog turns into segments of a given time interval (specified in the app config)
        page = request.args.get("page", 1, type=int)  # default page is 1
        (
            page_items,
            next_url,
            prev_url,
            first_url,
            last_url,
            total_pages,
            start_time,
        ) = self.get_items_for_this_page(page, segments)


@bp.route("/annotate_social_media/<int:dataset_id>")
@login_required
def annotate_sm(dataset_id):
    """This is the annotations page for social media datasets"""
    dataset = Dataset.query.get_or_404(
        dataset_id
    )  # fetch the dataset from the database
    return render_template("annotate/annotate_sm.html", dataset=dataset)
