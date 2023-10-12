"""
Functional tests for the annotate blueprint.
Psychotherapy session dataset annotation page.
Tests specific to the therapist role.
"""
from flask_login import current_user
from flask import url_for
from bs4 import BeautifulSoup
import pytest
from app.models import PSAnnotationTherapist, EvidenceTherapist
from tests.functional.utils import create_segment_level_annotation_therapist
import re
from app.utils import (
    SubLabelsATherapist,
    SubLabelsBTherapist,
    SubLabelsCTherapist,
    LabelStrengthDTherapist,
    LabelNamesTherapist,
)


@pytest.mark.dependency()
def test_valid_segment_level_annotation_therapist(test_client):
    """
    GIVEN a Flask application configured for testing and a dataset with psychotherapy dialog turns
    WHEN the '/annotate_psychotherapy' page is requested (POST) with a valid annotation for the therapist at the segment level
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

    # check that the "therapist" button is present in page 1
    # the button is used to toggle the annotation form
    page = 1
    url = url_for("annotate.annotate_ps", dataset_id=dataset_id, page=page)
    response = test_client.get(url)
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, "html.parser")
    therapist_button = soup.find("button", id="btn_therapist")
    assert therapist_button is not None
    # check that the annotation form for the therapist is present
    therapist_form = soup.find("form", id="form_therapist")
    assert therapist_form is not None

    # submit the annotation for the therapist
    page = 1
    url = url_for("annotate.annotate_ps", dataset_id=dataset_id, page=page)
    (
        data,
        events_a,
        events_b,
        events_c,
        events_d,
        events_e,
    ) = create_segment_level_annotation_therapist(soup)
    response = test_client.post(
        url,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Your annotations have been saved" in response.data

    # check that the annotation has been saved to the database
    annotation = PSAnnotationTherapist.query.filter_by(
        id_dataset=dataset_id,
    ).first()
    assert annotation is not None
    assert annotation.label_a == SubLabelsATherapist.emotional
    assert annotation.label_b == SubLabelsBTherapist.reframing
    assert annotation.comment_a == "test comment A"
    assert annotation.comment_summary == "test comment summary therapist"

    # test that the events submitted as evidence for the different labels
    # have been saved to the database
    evidence = EvidenceTherapist.query.filter_by(
        id_ps_annotation_therapist=annotation.id,
        label=LabelNamesTherapist.label_b,
    ).all()
    assert evidence is not None
    ids = [event.id_ps_dialog_event for event in evidence]
    assert ids == events_b

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.dependency(depends=["test_valid_segment_level_annotation_therapist"])
def test_retrieve_existing_annotations_therapist(test_client):
    """
    GIVEN a Flask application configured for testing and a dataset with psychotherapy dialog turns
    WHEN the '/annotate_psychotherapy' page is requested (GET) with a valid annotation for the therapist at the segment level
    THEN check the response is valid and the existing annotations are pre-populated in the therapist form
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
        "Annotations for the therapist for some or all speech turns on this page have already been submitted"
        in normalized_response
    )

    # check the form fields for the therapist
    soup = BeautifulSoup(response.data, "html.parser")
    comment_field = soup.find("textarea", id="comment_a_therapist")
    assert comment_field is not None
    assert (comment_field.get_text()).strip("\r\n ").lstrip() == "test comment A"
    select_field = soup.find("select", id="label_c_therapist")
    assert select_field is not None
    assert (
        select_field.find("option", selected=True).get_text()
        == SubLabelsCTherapist.exploration.value
    )
    select_field = soup.find("select", id="strength_d_therapist")
    assert select_field is not None
    assert (
        select_field.find("option", selected=True).get_text()
        == LabelStrengthDTherapist.low.value
    )
    comment_field = soup.find("textarea", id="comment_summary_therapist")
    assert comment_field is not None
    assert (comment_field.get_text()).strip(
        "\r\n "
    ).lstrip() == "test comment summary therapist"

    # check the evidence is pre-populated correctly
    # label B
    evidence = (
        EvidenceTherapist.query.filter_by(
            label=LabelNamesTherapist.label_b,
        )
        .order_by("id_ps_dialog_event")
        .all()
    )  # fetch from DB
    select_field = soup.find("select", id="relevant_events_b_therapist")
    assert select_field is not None
    selected_options = select_field.find_all("option", selected=True)
    selected_ids = [int(option.get_text()) for option in selected_options]
    assert selected_ids == [event.dialog_event.event_n for event in evidence]

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
