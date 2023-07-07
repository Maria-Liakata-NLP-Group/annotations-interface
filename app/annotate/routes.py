from app.annotate import bp
from flask import render_template
from flask_login import login_required
from models import Dataset


@bp.route("/annotate_ps/<int:dataset_id>")
@login_required
def annotate_ps(dataset_id):
    """This is the annotations page for psychotherapy datasets"""
    dataset = Dataset.query.get_or_404(
        dataset_id
    )  # fetch the dataset from the database
    return render_template("annotate_ps.html", dataset=dataset)
