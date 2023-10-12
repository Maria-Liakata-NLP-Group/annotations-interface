"""
Functional tests for the annotate blueprint.
Psychotherapy session dataset annotation page.
Tests specific to the dyad role.
"""
from flask_login import current_user
from flask import url_for
from bs4 import BeautifulSoup
import pytest
import re
from app.models import (
    PSAnnotationDyad,
    EvidenceDyad,
)
from app.utils import (
    SubLabelsADyad,
    SubLabelsBDyad,
    LabelStrengthADyad,
    LabelStrengthBDyad,
    LabelNamesDyad,
)
from tests.functional.utils import create_segment_level_annotation_dyad


@pytest.mark.dependency()
def test_valid_segment_level_annotation_dyad(test_client):
    """
    GIVEN a Flask application configured for testing and a dataset with psychotherapy dialog turns
    WHEN the '/annotate_psychotherapy' page is requested (POST) with a valid annotation for the dyad at the segment level
    THEN check the response is valid and the annotations are saved to the database
    """
    # log in to the app
    response = test_client.post(
        "/auth/login",
        data={"username": "annotator1", "password": "annotator1password"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # get the dataset id for the logged in user
    dataset = current_user.datasets.filter_by(name="Psychotherapy Dataset Test").all()
    dataset_id = dataset[0].id

    # check that the "dyad" button is present in page 1
    # the button is used to toggle the annotation form
    page = 1
    url = url_for("annotate.annotate_ps", dataset_id=dataset_id, page=page)
    response = test_client.get(url)
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, "html.parser")
    dyad_button = soup.find("button", id="btn_dyad")
    assert dyad_button is not None
    # check that the annotation form for the dyad is present
    dyad_form = soup.find("form", id="form_dyad")
    assert dyad_form is not None

    # submit the annotation for the dyad
    page = 1
    url = url_for("annotate.annotate_ps", dataset_id=dataset_id, page=page)
    data, events_a, events_b = create_segment_level_annotation_dyad(soup)
    response = test_client.post(
        url,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Your annotations have been saved" in response.data

    # check that the annotation has been saved to the database
    annotation = PSAnnotationDyad.query.filter_by(
        id_dataset=dataset_id,
    ).first()
    assert annotation is not None
    assert annotation.label_a == SubLabelsADyad.tasks_goals
    assert annotation.label_b == SubLabelsBDyad.withdrawal
    assert annotation.strength_a == LabelStrengthADyad.low
    assert annotation.strength_b == LabelStrengthBDyad.medium
    assert annotation.comment_a == "test comment A"
    assert annotation.comment_summary == "test comment summary dyad"

    # test that the events submitted as evidence for the different labels
    # have been saved to the database
    evidence = EvidenceDyad.query.filter_by(
        id_ps_annotation_dyad=annotation.id,
        label=LabelNamesDyad.label_a,
    ).all()
    assert evidence is not None
    ids = [event.id_ps_dialog_event for event in evidence]
    assert ids == events_a

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.dependency(
    depends=["test_valid_segment_level_annotation_dyad"],
)
def test_retrieve_existing_annotations_dyad(test_client):
    """
    GIVEN a Flask application configured for testing and a dataset with psychotherapy dialog turns
    WHEN the '/annotate_psychotherapy' page is requested (GET) with a valid annotation for the dyad at the segment level
    THEN check the response is valid and the existing annotations are pre-populated in the dyad form
    """
    # log in to the app
    response = test_client.post(
        "/auth/login",
        data={"username": "annotator1", "password": "annotator1password"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # get the dataset id for the logged in user
    dataset = current_user.datasets.filter_by(name="Psychotherapy Dataset Test").all()
    dataset_id = dataset[0].id

    # test that the annotations form for page 1 is pre-populated with the existing annotations
    page = 1
    url = url_for("annotate.annotate_ps", dataset_id=dataset_id, page=page)
    response = test_client.get(url)
    assert response.status_code == 200

    # normalize the response to remove extra whitespace
    normalized_response = re.sub(r"\s+", " ", response.text)
    assert (
        "Annotations for the dyad for some or all speech turns on this page have already been submitted"
        in normalized_response
    )

    # check the form fields for the dyad
    soup = BeautifulSoup(response.data, "html.parser")
    comment_field = soup.find("textarea", id="comment_a_dyad")
    assert comment_field is not None
    assert (comment_field.get_text()).strip("\r\n ").lstrip() == "test comment A"
    select_field = soup.find("select", id="label_a_dyad")
    assert select_field is not None
    assert (
        select_field.find("option", selected=True).get_text()
        == SubLabelsADyad.tasks_goals.value
    )
    select_field = soup.find("select", id="strength_b_dyad")
    assert select_field is not None
    assert (
        select_field.find("option", selected=True).get_text()
        == LabelStrengthBDyad.medium.value
    )
    comment_field = soup.find("textarea", id="comment_summary_dyad")
    assert comment_field is not None
    assert (comment_field.get_text()).strip(
        "\r\n "
    ).lstrip() == "test comment summary dyad"

    # check the evidence is pre-populated correctly
    # label A
    evidence = (
        EvidenceDyad.query.filter_by(
            label=LabelNamesDyad.label_a,
        )
        .order_by("id_ps_dialog_event")
        .all()
    )
    select_field = soup.find("select", id="relevant_events_a_dyad")
    assert select_field is not None
    selected_options = select_field.find_all("option", selected=True)
    selected_ids = [int(option.get_text()) for option in selected_options]
    assert selected_ids == [event.dialog_event.event_n for event in evidence]

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
