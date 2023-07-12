from app.annotate import bp
from flask import render_template, request, url_for, current_app
from flask_login import login_required
from app.models import Dataset
from app.annotate.utils import split_dialog_turns, get_events_from_sections


@bp.route("/annotate_psychotherapy/<int:dataset_id>")
@login_required
def annotate_ps(dataset_id):
    """This is the annotations page for psychotherapy datasets"""
    dataset = Dataset.query.get_or_404(
        dataset_id
    )  # fetch the dataset from the database
    dialog_turns = dataset.dialog_turns.order_by(
        "timestamp"
    ).all()  # fetch all dialog turns associated with the dataset
    # split the dialog turns into sections of five minutes
    app_config = current_app.config  # Get the app config
    try:
        sections = split_dialog_turns(
            dialog_turns, time_interval=app_config["PS_MINS_PER_PAGE"] * 60
        )
        # get the events corresponding to each section
        events = get_events_from_sections(sections)  # a list of lists
        # get the page number from the request
        page = request.args.get("page", 1, type=int)  # default page is 1
        page_items = events[page - 1]  # get the events for the current page
        has_prev = page > 1  # check if there is a previous page
        has_next = page < len(events)  # check if there is a next page
        if has_prev:
            prev_url = url_for(
                "annotate.annotate_ps", dataset_id=dataset_id, page=page - 1
            )
        else:
            prev_url = None
        if has_next:
            next_url = url_for(
                "annotate.annotate_ps", dataset_id=dataset_id, page=page + 1
            )
        else:
            next_url = None
        return render_template(
            "annotate/annotate_ps.html",
            dataset_name=dataset.name,
            page_items=page_items,
            next_url=next_url,
            prev_url=prev_url,
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
