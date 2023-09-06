"""
Functional tests for the `annotate` blueprint.
Psychotherapy session dataset annotation page.
"""
from flask_login import current_user
from flask import url_for
from bs4 import BeautifulSoup
import pytest
from app.models import PSDialogTurnAnnotation
from tests.functional.utils import (
    create_segment_level_annotation_client,
    create_segment_level_annotation_therapist,
)
import re
from app.utils import (
    Speaker,
    SubLabelsAClient,
    SubLabelsATherapist,
    SubLabelsBClient,
    SubLabelsBTherapist,
    SubLabelsC,
    LabelStrength,
)


@pytest.mark.dependency(
    depends=["tests/unit/test_upload_parsers.py::test_psychotherapy_df_to_sql"],
    scope="session",
)
def test_annotate_ps_valid_login(test_client, insert_ps_dialog_turns):
    """
    GIVEN a Flask application configured for testing and a dataset with psychotherapy dialog turns
    WHEN the '/annotate_psychotherapy' page is requested (GET) after logging in
    THEN check the response is valid, contains expected data and the pager is present
    """
    # log in to the app
    response = test_client.post(
        "/auth/login",
        data={"username": "annotator1", "password": "annotator1password"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Hi, annotator1" in response.data

    # get the dataset id for the logged in user
    dataset = current_user.datasets.filter_by(name="Psychotherapy Dataset Test").all()
    dataset_id = dataset[0].id

    # check the first annotation page for this dataset
    response = test_client.get("/annotate/annotate_psychotherapy/" + str(dataset_id))
    assert response.status_code == 200
    assert b"Annotating psychotherapy session" in response.data
    assert b"Psychotherapy Dataset Test" in response.data
    assert b"Time since start of session:" in response.data
    assert b"Client:" in response.data
    assert b"Therapist:" in response.data
    # check that the pager is present
    soup = BeautifulSoup(response.data, "html.parser")
    pager = soup.find("ul", class_="pager")
    assert pager is not None
    # previous button should be disabled
    previous_button = pager.find("li", class_="previous")
    assert previous_button is not None
    assert "disabled" in previous_button.attrs["class"]
    # next button should not be disabled
    next_button = pager.find("li", class_="next")
    assert next_button is not None
    assert "disabled" not in next_button.attrs["class"]
    # first button should be disabled
    first_button = pager.find("li", class_="first")
    assert first_button is not None
    assert "disabled" in first_button.attrs["class"]
    # last button should not be disabled
    last_button = pager.find("li", class_="last")
    assert last_button is not None
    assert "disabled" not in last_button.attrs["class"]

    # move to the next page (page 2)
    response = test_client.get(
        "/annotate/annotate_psychotherapy/" + str(dataset_id) + "?page=2"
    )
    assert response.status_code == 200
    assert b"Annotating psychotherapy session" in response.data
    assert b"Psychotherapy Dataset Test" in response.data
    assert b"Time since start of session:" in response.data
    assert b"Client:" in response.data
    assert b"Therapist:" in response.data
    # check that the pager is present
    soup = BeautifulSoup(response.data, "html.parser")
    pager = soup.find("ul", class_="pager")
    assert pager is not None
    # previous button should not be disabled
    previous_button = pager.find("li", class_="previous")
    assert previous_button is not None
    assert "disabled" not in previous_button.attrs["class"]
    # next button should not be disabled
    next_button = pager.find("li", class_="next")
    assert next_button is not None
    assert "disabled" not in next_button.attrs["class"]
    # first button should not be disabled
    first_button = pager.find("li", class_="first")
    assert first_button is not None
    assert "disabled" not in first_button.attrs["class"]
    # last button should not be disabled
    last_button = pager.find("li", class_="last")
    assert last_button is not None
    assert "disabled" not in last_button.attrs["class"]

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.order(after="test_annotate_ps_valid_login")
@pytest.mark.dependency()
@pytest.mark.dependency(
    depends=["tests/unit/test_upload_parsers.py::test_psychotherapy_df_to_sql"],
    scope="session",
)
def test_annotate_ps_valid_segment_level_annotation(test_client):
    """
    GIVEN a Flask application configured for testing and a dataset with psychotherapy dialog turns
    WHEN the '/annotate_psychotherapy' page is requested (POST) with a valid annotation at the segment level
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

    # check that the "client" and "therapist" buttons are present in page 1
    # these buttons are used to toggle the annotation forms
    page = 1
    url = url_for("annotate.annotate_ps", dataset_id=dataset_id, page=page)
    response = test_client.get(url)
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, "html.parser")
    client_button = soup.find("button", id="btn_client")
    assert client_button is not None
    therapist_button = soup.find("button", id="btn_therapist")
    assert therapist_button is not None
    # check that the annotation forms for the client and therapist are present
    client_form = soup.find("form", id="form_client")
    assert client_form is not None
    therapist_form = soup.find("form", id="form_therapist")
    assert therapist_form is not None

    # submit the annotation for the client
    data = create_segment_level_annotation_client()
    response = test_client.post(
        url,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Your annotations have been saved" in response.data

    # check that the annotation has been saved to the database
    # and that the labels for the therapist for this annotation are null
    annotation = PSDialogTurnAnnotation.query.filter_by(
        id_dataset=dataset_id,
        speaker=Speaker.client.name,
    ).first()
    assert annotation is not None
    assert annotation.label_a_client == SubLabelsAClient.excitement
    assert annotation.label_b_client == SubLabelsBClient.security
    assert annotation.label_a_therapist is None
    assert annotation.label_b_therapist is None
    assert annotation.strength_a == LabelStrength.high
    assert annotation.comment_a == "test comment A"

    # submit the annotation for the therapist
    data = create_segment_level_annotation_therapist()
    response = test_client.post(
        url,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Your annotations have been saved" in response.data

    # check that the annotation has been saved to the database
    # and that the labels for the client for this annotation are null
    annotation = PSDialogTurnAnnotation.query.filter_by(
        id_dataset=dataset_id,
        speaker=Speaker.therapist.name,
    ).first()
    assert annotation is not None
    assert annotation.label_a_therapist == SubLabelsATherapist.emotional
    assert annotation.label_b_therapist == SubLabelsBTherapist.reframing
    assert annotation.label_a_client is None
    assert annotation.label_b_client is None
    assert annotation.comment_a == "test comment A"

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.dependency(
    depends=["test_annotate_ps_valid_segment_level_annotation"],
)
@pytest.mark.order(after="test_annotate_ps_valid_segment_level_annotation")
def test_annotate_ps_retrieve_existing_annotations(test_client):
    """
    GIVEN a Flask application configured for testing and a dataset with psychotherapy dialog turns
    WHEN the '/annotate_psychotherapy' page is requested (GET) with a valid annotation at the segment level
    THEN check the response is valid and the existing annotations are pre-populated in the form
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
    assert (
        "Annotations for the therapist for some or all speech turns on this page have already been submitted"
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
        select_field.find("option", selected=True).get_text() == LabelStrength.low.value
    )

    # check the form fields for the therapist
    comment_field = soup.find("textarea", id="comment_a_therapist")
    assert comment_field is not None
    assert (comment_field.get_text()).strip("\r\n ").lstrip() == "test comment A"
    select_field = soup.find("select", id="label_c_therapist")
    assert select_field is not None
    assert (
        select_field.find("option", selected=True).get_text()
        == SubLabelsC.sublabel3.value
    )
    select_field = soup.find("select", id="strength_d_therapist")
    assert select_field is not None
    assert (
        select_field.find("option", selected=True).get_text()
        == LabelStrength.high.value
    )

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.order(after="test_annotate_ps_retrieve_existing_annotations")
def test_annotate_ps_comment_is_compulsory_if_label_is_other(test_client):
    """
    GIVEN a Flask application configured for testing and a dataset with psychotherapy dialog turns
    WHEN the '/annotate_psychotherapy' page is requested (POST) with an invalid annotation at the segment level
    THEN check a validation error is raised if the label is "Other" and the comment is empty
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
    page = 1
    url = url_for("annotate.annotate_ps", dataset_id=dataset_id, page=page)
    # set the label to "Other" and the comment to empty
    data = create_segment_level_annotation_client()
    data["label_a_client"] = SubLabelsAClient.other.value
    data["comment_a_client"] = ""
    response = test_client.post(url, data=data, follow_redirects=True)
    assert response.status_code == 200
    normalized_response = re.sub(r"\s+", " ", response.text)
    assert "Your annotations have been saved" not in normalized_response
    assert "If you select Other, please provide a comment." in normalized_response
