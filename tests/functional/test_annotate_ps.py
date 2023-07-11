"""
Functional tests for the `annotate` blueprint.
Psychotherapy session dataset annotation page.
"""
from flask_login import current_user
from bs4 import BeautifulSoup
import pytest


@pytest.mark.order(
    after="tests/unit/test_upload_parsers.py::test_psychotherapy_df_to_sql"
)
@pytest.mark.dependency(
    depends=["tests/unit/test_upload_parsers.py::test_psychotherapy_df_to_sql"],
    scope="session",
)
def test_annotate_ps_valid_login(test_client, insert_users, insert_ps_dialog_turns):
    """
    GIVEN a Flask application configured for testing and a dataset with psychotherapy dialog turns
    WHEN the '/annotate_psychotherapy' page is requested (GET) after logging in
    THEN check the response is valid and contains expected data
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

    # check the first annotation page for this dataset
    response = test_client.get("/annotate/annotate_psychotherapy/" + str(dataset_id))
    assert response.status_code == 200
    assert b"Annotating psychotherapy session" in response.data
    assert b"Psychotherapy Dataset Test" in response.data
    assert b"Client:" in response.data
    assert b"Therapist:" in response.data
    # check that the pager is present
    soup = BeautifulSoup(response.data, "html.parser")
    pager = soup.find("ul", class_="pager")
    assert pager is not None
    previous_button = pager.find("li", class_="previous")
    assert previous_button is not None
    next_button = pager.find("li", class_="next")
    assert next_button is not None

    # move to the next page
    response = test_client.get(
        "/annotate/annotate_psychotherapy/" + str(dataset_id) + "?page=2"
    )
    assert response.status_code == 200
    assert b"Annotating psychotherapy session" in response.data
    assert b"Psychotherapy Dataset Test" in response.data
    assert b"Client:" in response.data
    assert b"Therapist:" in response.data

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
