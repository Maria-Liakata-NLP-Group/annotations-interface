"""
Functional tests for the annotate blueprint.
Psychotherapy session dataset annotation page.
Tests specific for client annotations.
"""
from flask_login import current_user
from flask import url_for
from bs4 import BeautifulSoup
from app.models import PSAnnotationClient, EvidenceClient
from tests.functional.utils import create_segment_level_annotation_client
import re
from app.utils import (
    SubLabelsAClient,
    SubLabelsBClient,
    SubLabelsEClient,
    SubLabelsFClient,
    LabelStrengthAClient,
    LabelStrengthCClient,
    LabelStrengthFClient,
    LabelNamesClient,
)
import pytest


def test_default_values_for_label_f_client(test_client):
    """
    GIVEN a Flask application configured for testing and a dataset with psychotherapy dialog turns
    WHEN the '/annotate_psychotherapy' page is requested (GET) without any existing annotations
    THEN check the default value for label_f_client and strength_f_client is "no change"
    """

    # log in to the app
    response = test_client.post(
        "/auth/login",
        data={"username": "annotator1", "password": "annotator1password"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # get the dataset id for the logged in user
    dataset = current_user.datasets.filter_by(name="Psychotherapy Dataset Test").first()
    dataset_id = dataset.id

    # check that the "label_f_client" and "strength_f_client"
    # fields have the default value "no change"
    page = 1
    url = url_for("annotate.annotate_ps", dataset_id=dataset_id, page=page)
    response = test_client.get(url)
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")
    select_field = soup.find("select", id="label_f_client")
    assert select_field is not None
    assert (
        select_field.find("option", selected=True).get_text()
        == SubLabelsFClient.no_change.value
    )

    select_field = soup.find("select", id="strength_f_client")
    assert select_field is not None
    assert (
        select_field.find("option", selected=True).get_text()
        == LabelStrengthFClient.no_change.value
    )

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.dependency()
def test_valid_segment_level_annotation_client(test_client):
    """
    GIVEN a Flask application configured for testing and a dataset with psychotherapy dialog turns
    WHEN the '/annotate_psychotherapy' page is requested (POST) with a valid annotation for the client at the segment level
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

    # check that the "client" button is present in page 1
    # the button is used to toggle the annotation form
    page = 1
    url = url_for("annotate.annotate_ps", dataset_id=dataset_id, page=page)
    response = test_client.get(url)
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, "html.parser")
    client_button = soup.find("button", id="btn_client")
    assert client_button is not None
    # check that the annotation form for the client is present
    client_form = soup.find("form", id="form_client")
    assert client_form is not None

    # submit the annotation for the client
    (
        data,
        events_a,
        events_b,
        events_c,
        events_d,
        events_e,
        start_event_f,
        end_event_f,
    ) = create_segment_level_annotation_client(soup)
    response = test_client.post(
        url,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Your annotations have been saved" in response.data

    # check that the annotation has been saved to the database
    annotation = PSAnnotationClient.query.filter_by(
        id_dataset=dataset_id,
    ).first()
    assert annotation is not None
    assert annotation.label_a == SubLabelsAClient.excitement
    assert annotation.label_b == SubLabelsBClient.security
    assert annotation.label_e == SubLabelsEClient.insight
    assert annotation.label_f == SubLabelsFClient.switch
    assert annotation.strength_a == LabelStrengthAClient.highly_maladaptive
    assert annotation.strength_f == LabelStrengthFClient.some_improvement
    assert annotation.comment_a == "test comment A"
    assert annotation.comment_summary == "test comment summary client"

    # test that the events submitted as evidence for the different labels
    # have been saved to the database
    evidence = EvidenceClient.query.filter_by(
        id_ps_annotation_client=annotation.id,
        label=LabelNamesClient.label_a,
    ).all()
    assert evidence is not None
    ids = [event.id_ps_dialog_event for event in evidence]
    assert ids == events_a

    evidence = EvidenceClient.query.filter_by(
        id_ps_annotation_client=annotation.id,
        label=LabelNamesClient.label_f,
    ).all()  # label_f is a special case - Moment of Change
    assert evidence is not None
    ids = [event.id_ps_dialog_event for event in evidence]
    assert ids == list(range(start_event_f, end_event_f + 1))

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.dependency(depends=["test_valid_segment_level_annotation_client"])
def test_retrieve_existing_annotations_client(test_client):
    """
    GIVEN a Flask application configured for testing and a dataset with psychotherapy dialog turns
    WHEN the '/annotate_psychotherapy' page is requested (GET) with a valid annotation for the client at the segment level
    THEN check the response is valid and the existing annotations are pre-populated in the client form
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
        "Annotations for the client for some or all speech turns on this page have already been submitted"
        in normalized_response
    )

    # check the form fields for the client
    soup = BeautifulSoup(response.data, "html.parser")
    select_field = soup.find("select", id="label_a_client")
    assert select_field is not None
    assert (
        select_field.find("option", selected=True).get_text()
        == SubLabelsAClient.excitement.value
    )
    select_field = soup.find("select", id="label_b_client")
    assert select_field is not None
    assert (
        select_field.find("option", selected=True).get_text()
        == SubLabelsBClient.security.value
    )
    comment_field = soup.find("textarea", id="comment_a_client")
    assert comment_field is not None
    assert (comment_field.get_text()).strip("\r\n ").lstrip() == "test comment A"
    select_field = soup.find("select", id="label_b_client")
    assert select_field is not None
    assert (
        select_field.find("option", selected=True).get_text()
        == SubLabelsBClient.security.value
    )
    select_field = soup.find("select", id="strength_c_client")
    assert select_field is not None
    assert (
        select_field.find("option", selected=True).get_text()
        == LabelStrengthCClient.moderately_adaptive.value
    )
    comment_field = soup.find("textarea", id="comment_summary_client")
    assert comment_field is not None
    assert (comment_field.get_text()).strip(
        "\r\n "
    ).lstrip() == "test comment summary client"
    select_field = soup.find("select", id="label_f_client")
    assert select_field is not None
    assert (
        select_field.find("option", selected=True).get_text()
        == SubLabelsFClient.switch.value
    )
    select_field = soup.find("select", id="strength_f_client")
    assert select_field is not None
    assert (
        select_field.find("option", selected=True).get_text()
        == LabelStrengthFClient.some_improvement.value
    )

    # check the evidence is pre-populated correctly
    # label A
    evidence = (
        EvidenceClient.query.filter_by(
            label=LabelNamesClient.label_a,
        )
        .order_by("id_ps_dialog_event")
        .all()
    )  # fetch from DB
    select_field = soup.find("select", id="relevant_events_a_client")
    assert select_field is not None
    selected_options = select_field.find_all("option", selected=True)
    selected_ids = [int(option.get_text()) for option in selected_options]
    assert selected_ids == [event.dialog_event.event_n for event in evidence]

    # label F - MoC
    evidence = (
        EvidenceClient.query.filter_by(
            label=LabelNamesClient.label_f,
        )
        .order_by("id_ps_dialog_event")
        .all()
    )  # fetch from DB
    start_event_f = evidence[0].dialog_event.event_n
    end_event_f = evidence[-1].dialog_event.event_n
    select_field = soup.find("select", id="start_event_f_client")
    assert select_field is not None
    assert int(select_field.find("option", selected=True).get_text()) == start_event_f
    select_field = soup.find("select", id="end_event_f_client")
    assert select_field is not None
    assert int(select_field.find("option", selected=True).get_text()) == end_event_f

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
