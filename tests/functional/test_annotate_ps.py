"""
Functional tests for the `annotate` blueprint.
Psychotherapy session dataset annotation page.
"""
from flask_login import current_user
from flask import url_for
from bs4 import BeautifulSoup
import pytest
from tests.functional.utils import (
    create_segment_level_annotation_client,
)
import re
from app.utils import SubLabelsAClient


@pytest.mark.dependency(
    depends=["tests/unit/test_upload_parsers.py::test_psychotherapy_df_to_sql"],
    scope="session",
)
@pytest.mark.dependency()
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
    soup = BeautifulSoup(test_client.get(url).data, "html.parser")
    data = create_segment_level_annotation_client(soup)[0]
    data["label_a_client"] = SubLabelsAClient.other.value
    data["comment_a_client"] = ""
    response = test_client.post(url, data=data, follow_redirects=True)
    assert response.status_code == 200
    normalized_response = re.sub(r"\s+", " ", response.text)
    assert "Your annotations have been saved" not in normalized_response
    assert "If you select Other, please provide a comment." in normalized_response
