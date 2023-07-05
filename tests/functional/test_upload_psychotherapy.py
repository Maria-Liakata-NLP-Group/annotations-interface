"""
Functional tests for the upload (`upload`) blueprint.
Psychotherapy session dataset upload page.
"""
from app.models import User, Dataset, Psychotherapy
from bs4 import BeautifulSoup
from datetime import datetime


def test_upload_psychotherapy_login_required(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload_psychotherapy' page is requested (GET) without being logged in
    THEN check the response is valid and the user is redirected to the login page
    """
    response = test_client.get("/upload/upload_psychotherapy")
    assert response.status_code == 302  # check redirect
    assert "/auth/login" in response.headers["Location"]


def test_upload_psychotherapy_valid_login(test_client, insert_users):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload_psychotherapy' page is requested (GET) after logging in
    THEN check the response is valid
    """
    # log in to the app
    response = test_client.post(
        "/auth/login",
        data={"username": "admin1", "password": "adminpassword1"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # check upload page
    response = test_client.get("/upload/upload_psychotherapy")
    assert response.status_code == 200
    assert b"Upload new psychotherapy session dataset" in response.data
    assert b"Dataset name" in response.data
    assert b"description" in response.data
    assert b'type="submit"' in response.data  # check submit button
    assert b'type="file"' in response.data  # check file upload button

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


def test_upload_psychotherapy_valid_dataset(test_client, insert_users):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload_psychotherapy' page is requested (POST) with a valid dataset (with two annotators)
    THEN check the response is valid and the dataset is added to the database correctly
    """
    # log in to the app
    response = test_client.post(
        "/auth/login",
        data={"username": "admin1", "password": "adminpassword1"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # check upload page
    response = test_client.get("/upload/upload_psychotherapy")
    assert response.status_code == 200

    # upload a valid dataset
    with open("tests/data/psychotherapy_example_lorem.pickle", "rb") as handle:
        response = test_client.post(
            "/upload/upload_psychotherapy",
            data={
                "name": "test_dataset",
                "description": "test description",
                "annotators": [
                    User.query.filter_by(username="admin1").first().id,
                    User.query.filter_by(username="annotator1").first().id,
                ],
                "file": (handle, "psychotherapy_example_lorem.pickle"),
            },
            follow_redirects=True,
        )
    assert response.status_code == 200
    assert b"File uploaded successfully" in response.data

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200

    # check dataset is in database, and has correct number of posts and replies
    dataset = Dataset.query.filter_by(name="test_dataset").first()
    admin1 = User.query.filter_by(username="admin1").first()
    annotator1 = User.query.filter_by(username="annotator1").first()

    assert dataset
    assert dataset.name == "test_dataset"
    assert dataset.description == "test description"
    assert dataset.id_author == admin1.id
    assert dataset.annotators.all() == [admin1, annotator1]
    assert dataset.type.value == "Psychotherapy Session"

    psychotherapy = Psychotherapy.query.filter_by(id_dataset=dataset.id).all()
    assert len(psychotherapy) == 228
    psychotherapy[
        100
    ].event_id == 100  # event id is the row index in the original dataframe
    psychotherapy[100].id == 101  # this is the row index of the SQL table
    psychotherapy[100].event_text == "Amet consectetur quiquia dolor sit."
    psychotherapy[100].event_speaker == "Client"
    psychotherapy[100].date == datetime.strptime("6/18/2015", "%m/%d/%Y").date()


def test_upload_psychotherapy_invalid_dataset(test_client, insert_users):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload_psychotherapy' page is requested (POST) with an invalid dataset
    THEN check a HTTP 400 error is raised with a helpful error message, and
    the dataset is not added to the database
    """
    # log in to the app
    response = test_client.post(
        "/auth/login",
        data={"username": "admin1", "password": "adminpassword1"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # check upload page
    response = test_client.get("/upload/upload_psychotherapy")
    assert response.status_code == 200

    # upload an invalid dataset
    with open("tests/data/timelines_example_lorem.pickle", "rb") as handle:
        response = test_client.post(
            "/upload/upload_psychotherapy",
            data={
                "name": "invalid_dataset",
                "description": "test description",
                "annotators": User.query.filter_by(username="admin1").first().id,
                "file": (handle, "timelines_example_lorem.pickle"),
            },
            follow_redirects=True,
        )
    assert response.status_code == 400
    assert b"dataset provided could not be added to the database" in response.data

    # check the dataset is not in the database
    dataset = Dataset.query.filter_by(name="invalid_dataset").first()
    assert dataset is None

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


def test_upload_based_on_role(test_client, insert_users):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload_psychotherapy' page is requested (GET) after logging in as a user with a role
    THEN check the 'Annotator' SelectField is populated with the correct users
    """
    # log in to the app as a user with the 'annotator' role
    response = test_client.post(
        "/auth/login",
        data={"username": "annotator1", "password": "annotatorpassword1"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # check upload page
    response = test_client.get("/upload/upload_psychotherapy")
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")  # parse HTML
    select_element = soup.find(
        "select", id="annotators"
    )  # find the 'Annotator' SelectField
    expected_options = [
        "annotator1"
    ]  # the annotator should only be able to see themselves
    actual_options = [option.text for option in select_element.find_all("option")]
    assert actual_options == expected_options

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200

    # log in to the app as a user with the 'admin' role
    response = test_client.post(
        "/auth/login",
        data={"username": "admin1", "password": "adminpassword1"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # check upload page
    response = test_client.get("/upload/upload_psychotherapy")
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")  # parse HTML
    select_element = soup.find(
        "select", id="annotators"
    )  # find the 'Annotator' SelectField
    expected_options = [
        "annotator1",
        "admin1",
    ]  # the admin should be able to see all users
    actual_options = [option.text for option in select_element.find_all("option")]
    assert sorted(actual_options) == sorted(expected_options)

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
