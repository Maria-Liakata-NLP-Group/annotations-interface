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
    create_psy_annotation_form,
    assign_evidence_dynamic_choices,
)
from flask.views import View


class AnnotatePSView(View):
    """Class-based view for the annotations page for psychotherapy datasets"""

    methods = ["GET", "POST"]
    decorators = [login_required]

    def __init__(self, template: str):
        """Initialize the view with the specified template"""
        self.template = template

    def get_items_for_this_page(self, page: int, segments: list):
        """Get the items for the current page"""
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
        ) = get_page_items(page, events, self.dataset.id)
        return (
            page_items,
            next_url,
            prev_url,
            first_url,
            last_url,
            total_pages,
            start_time,
        )

    def create_form(self, dialog_turns: list, page_items: list, speaker: Speaker):
        """Create the annotations form for the specified speaker"""
        annotations = fetch_dialog_turn_annotations(dialog_turns, speaker)
        form = create_psy_annotation_form(annotations, speaker)
        form = assign_evidence_dynamic_choices(form, page_items, speaker)
        return form, annotations

    def dispatch_request(self, dataset_id: int):
        """This method is the equivalent of the view function"""
        self.dataset = Dataset.query.get_or_404(dataset_id)
        app_config = current_app.config
        segments = split_dialog_turns(
            self.dataset.dialog_turns.order_by("timestamp").all(),
            time_interval=app_config["PS_MINS_PER_PAGE"] * 60,
        )  # split the dialog turns into segments
        page = request.args.get(
            "page", 1, type=int
        )  # get the page number from the url (default is 1)
        (
            page_items,
            next_url,
            prev_url,
            first_url,
            last_url,
            total_pages,
            start_time,
        ) = self.get_items_for_this_page(page, segments)
        dialog_turns = segments[page - 1]  # get the dialog turns for the current page
        form_client, annotations_client = self.create_form(
            dialog_turns, page_items, Speaker.client
        )
        form_therapist, annotations_therapist = self.create_form(
            dialog_turns, page_items, Speaker.therapist
        )
        form_dyad, annotations_dyad = self.create_form(
            dialog_turns, page_items, Speaker.dyad
        )
        if "submit_form_client" in request.form:
            # if the client form is submitted
            if form_client.validate_on_submit():
                try:
                    new_dialog_turn_annotation_to_db(
                        form_client,
                        Speaker.client,
                        self.dataset,
                        dialog_turns=segments[page - 1],
                    )
                except Exception as e:
                    print(e)
                    db.session.rollback()
                    abort(500)
                db.session.commit()
                flash("Your annotations have been saved.", "success")
                return redirect(
                    url_for(
                        "annotate.annotate_ps", dataset_id=self.dataset.id, page=page
                    )
                )
        elif "submit_form_therapist" in request.form:
            # if the therapist form is submitted
            if form_therapist.validate_on_submit():
                try:
                    new_dialog_turn_annotation_to_db(
                        form_therapist,
                        Speaker.therapist,
                        self.dataset,
                        dialog_turns=segments[page - 1],
                    )
                except Exception as e:
                    print(e)
                    db.session.rollback()
                    abort(500)
                db.session.commit()
                flash("Your annotations have been saved.", "success")
                return redirect(
                    url_for(
                        "annotate.annotate_ps", dataset_id=self.dataset.id, page=page
                    )
                )
        elif "submit_form_dyad" in request.form:
            # if the dyad form is submitted
            if form_dyad.validate_on_submit():
                try:
                    new_dialog_turn_annotation_to_db(
                        form_dyad,
                        Speaker.dyad,
                        self.dataset,
                        dialog_turns=segments[page - 1],
                    )
                except Exception as e:
                    print(e)
                    db.session.rollback()
                    abort(500)
                db.session.commit()
                flash("Your annotations have been saved.", "success")
                return redirect(
                    url_for(
                        "annotate.annotate_ps", dataset_id=self.dataset.id, page=page
                    )
                )
        return render_template(
            self.template,
            dataset_name=self.dataset.name,
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


bp.add_url_rule(
    "/annotate_psychotherapy/<int:dataset_id>",
    view_func=AnnotatePSView.as_view(
        "annotate_ps", template="annotate/annotate_ps.html"
    ),
)


# create a route that will handle dynamic updates of the select field choices
@bp.route("/update_select_choices", methods=["POST"])
@login_required
def update_select_choices():
    """
    This route handles dynamic updates of a second select field
    based on the choice of the first select field.
    """
    # selected_value = request.form.get("selected_value")
    pass


@bp.route("/annotate_social_media/<int:dataset_id>")
@login_required
def annotate_sm(dataset_id):
    """This is the annotations page for social media datasets"""
    dataset = Dataset.query.get_or_404(
        dataset_id
    )  # fetch the dataset from the database
    return render_template("annotate/annotate_sm.html", dataset=dataset)
