"""
Functional tests for the `annotate` blueprint.
Psychotherapy session dataset annotation page.
"""
from app.models import Dataset
from flask_login import current_user


def test_annotate_ps_valid_login(test_client, insert_users, insert_datasets):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/annotate_psychotherapy' page is requested (GET) after logging in
    THEN check the response is valid
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

    # check annotation page for this dataset
    response = test_client.get("/annotate/annotate_psychotherapy/" + str(dataset_id))
    assert response.status_code == 200
    assert b"Annotating psychotherapy session" in response.data
    assert b"Psychotherapy Dataset Test" in response.data
