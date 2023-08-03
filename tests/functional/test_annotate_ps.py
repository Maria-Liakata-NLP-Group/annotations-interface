"""
Functional tests for the `annotate` blueprint.
Psychotherapy session dataset annotation page.
"""
from flask_login import current_user
from flask import url_for
from bs4 import BeautifulSoup
import pytest
from app.utils import (
    Speaker,
    LabelStrength,
    SubLabelsA,
    SubLabelsB,
    SubLabelsC,
    SubLabelsD,
    SubLabelsE,
)
from app.annotate.utils import split_dialog_turns


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


@pytest.mark.dependency(
    depends=["tests/unit/test_upload_parsers.py::test_psychotherapy_df_to_sql"],
    scope="session",
)
def test_annotate_ps_valid_dialog_turn_annotation(test_client, insert_ps_dialog_turns):
    """
    GIVEN a Flask application configured for testing and a dataset with psychotherapy dialog turns
    WHEN the '/annotate_psychotherapy' page is requested (POST) with valid dialog turn annotations
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

    # submit an annotation for the client
    client_data = {
        "form_client.label_a": SubLabelsA.sublabel1,
        "form_client.label_b": SubLabelsB.sublabel1,
        "form_client.label_c": SubLabelsC.sublabel1,
        "form_client.label_d": SubLabelsD.sublabel1,
        "form_client.label_e": SubLabelsE.sublabel1,
        "form_client.strength_a": LabelStrength.medium,
        "form_client.strength_b": LabelStrength.medium,
        "form_client.strength_c": LabelStrength.medium,
        "form_client.strength_d": LabelStrength.medium,
        "form_client.strength_e": LabelStrength.medium,
        "form_client.comment_a": "test comment",
        "form_client.comment_b": "test comment",
        "form_client.comment_c": "test comment",
        "form_client.comment_d": "test comment",
        "form_client.comment_e": "test comment",
        "speaker": Speaker.client,
    }
    response_client = test_client.post(url, data=client_data, follow_redirects=True)
    assert response_client.status_code == 200
