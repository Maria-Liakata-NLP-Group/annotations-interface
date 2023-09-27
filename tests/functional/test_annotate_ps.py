"""
Functional tests for the `annotate` blueprint.
Psychotherapy session dataset annotation page.
"""
from flask_login import current_user
from flask import url_for
from bs4 import BeautifulSoup
import pytest
from app.models import (
    PSAnnotationClient,
    PSAnnotationTherapist,
    PSAnnotationDyad,
    EvidenceClient,
)
from tests.functional.utils import (
    create_segment_level_annotation_client,
    create_segment_level_annotation_therapist,
    create_segment_level_annotation_dyad,
)
import re
from app.utils import (
    SubLabelsAClient,
    SubLabelsATherapist,
    SubLabelsADyad,
    SubLabelsBClient,
    SubLabelsBTherapist,
    SubLabelsBDyad,
    SubLabelsCTherapist,
    SubLabelsEClient,
    SubLabelsFClient,
    LabelStrengthAClient,
    LabelStrengthCClient,
    LabelStrengthDTherapist,
    LabelStrengthADyad,
    LabelStrengthBDyad,
    LabelStrengthFClient,
    LabelNamesClient,
)


@pytest.mark.dependency(
    depends=["tests/unit/test_upload_parsers.py::test_psychotherapy_df_to_sql"],
    scope="session",
)
def test_valid_login(test_client, insert_ps_dialog_turns):
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


@pytest.mark.order(after="test_default_values_for_label_f_client")
@pytest.mark.dependency()
@pytest.mark.dependency(
    depends=["tests/unit/test_upload_parsers.py::test_psychotherapy_df_to_sql"],
    scope="session",
)
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
    data = create_segment_level_annotation_client()
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
    assert len(evidence) == 2
    assert evidence[0].id_ps_dialog_event == 2
    assert evidence[1].id_ps_dialog_event == 4

    evidence = EvidenceClient.query.filter_by(
        id_ps_annotation_client=annotation.id,
        label=LabelNamesClient.label_f,
    ).all()
    assert evidence is not None
    assert len(evidence) == 3
    assert evidence[0].id_ps_dialog_event == 2
    assert evidence[1].id_ps_dialog_event == 3
    assert evidence[2].id_ps_dialog_event == 4

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.order(after="test_valid_segment_level_annotation_client")
@pytest.mark.dependency(
    depends=["tests/unit/test_upload_parsers.py::test_psychotherapy_df_to_sql"],
    scope="session",
)
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
    annotation = PSAnnotationTherapist.query.filter_by(
        id_dataset=dataset_id,
    ).first()
    assert annotation is not None
    assert annotation.label_a == SubLabelsATherapist.emotional
    assert annotation.label_b == SubLabelsBTherapist.reframing
    assert annotation.comment_a == "test comment A"
    assert annotation.comment_summary == "test comment summary therapist"

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.order(after="test_valid_segment_level_annotation_therapist")
@pytest.mark.dependency(
    depends=["tests/unit/test_upload_parsers.py::test_psychotherapy_df_to_sql"],
    scope="session",
)
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
    data = create_segment_level_annotation_dyad()
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

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.dependency(
    depends=["test_valid_segment_level_annotation_client"],
)
@pytest.mark.order(after="test_valid_segment_level_annotation_dyad")
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

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.dependency(
    depends=["test_valid_segment_level_annotation_therapist"],
)
@pytest.mark.order(after="test_retrieve_existing_annotations_client")
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

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.dependency(
    depends=["test_valid_segment_level_annotation_dyad"],
)
@pytest.mark.order(after="test_retrieve_existing_annotations_therapist")
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

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.order(after="test_retrieve_existing_annotations_dyad")
def test_comment_is_compulsory_if_label_is_other(test_client):
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


@pytest.mark.order(after="test_valid_login")
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
