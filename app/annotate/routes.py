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
    create_psy_annotation_form,
    assign_dynamic_choices,
)


class AnnotatePsy(View):
    """
    Class-based view for the annotation pages for psychotherapy datasets.
    Supports annotations for client, therapist and dyad.
    """

    methods = ["GET", "POST"]
    decorators = [login_required]

    def __init__(self):
        """Initialize the class with the speaker and template"""
        try:
            speaker = request.args.get("speaker", "client", type=str)
            self.speaker = Speaker(speaker)
        except ValueError:
            enum_names = [speaker.name for speaker in Speaker]
            print("Invalid speaker name. Valid names are: ", enum_names)
            abort(500)
        else:
            self.template = f"annotate/{self.speaker.name}_psy.html"

    def get_items_for_this_page(self, page, segments):
        """Get the events and urls for the pager for the current page"""
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
            page,
            events,
            self.dataset.id,
            self.speaker,
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
        """Create the form and fetch the annotations for the current page"""
        annotations = fetch_dialog_turn_annotations(dialog_turns, self.speaker)
        form = create_psy_annotation_form(annotations, self.speaker)
        form = assign_dynamic_choices(form, page_items, self.speaker)
        return form, annotations

    def dispatch_request(self, dataset_id):
        self.dataset = Dataset.query.get_or_404(dataset_id)  # fetch the dataset
        app_config = current_app.config
        segments = split_dialog_turns(
            self.dataset.dialog_turns.order_by("timestamp").all(),
            time_interval=app_config["PS_MINS_PER_PAGE"] * 60,
        )  # split the dialog turns into segments of a given time interval (specified in the app config)
        page = request.args.get("page", 1, type=int)  # default page is 1
        dialog_turns = segments[page - 1]
        (
            page_items,
            next_url,
            prev_url,
            first_url,
            last_url,
            total_pages,
            start_time,
        ) = self.get_items_for_this_page(page, segments)
        form, annotations = self.create_form(dialog_turns, page_items)
        if form.validate_on_submit():
            try:
                new_dialog_turn_annotation_to_db(
                    form, self.speaker, self.dataset, dialog_turns
                )
            except Exception as e:
                print(e)
                db.session.rollback()
                abort(500)
            else:
                db.session.commit()
                flash("Your annotations have been saved.", "success")
                return redirect(
                    url_for(
                        "annotate.annotate_psy",
                        dataset_id=self.dataset.id,
                        speaker=self.speaker.name,
                        page=page,
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
            annotations=annotations,
            form=form,
        )


bp.add_url_rule(
    "/annotate_psychotherapy/<int:dataset_id>",
    view_func=AnnotatePsy.as_view("annotate_psy"),
)


@bp.route("/annotate_social_media/<int:dataset_id>")
@login_required
def annotate_sm(dataset_id):
    """This is the annotations page for social media datasets"""
    dataset = Dataset.query.get_or_404(
        dataset_id
    )  # fetch the dataset from the database
    return render_template("annotate/annotate_sm.html", dataset=dataset)
