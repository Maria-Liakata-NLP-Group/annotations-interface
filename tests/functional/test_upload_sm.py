"""
Functional tests for the upload (`upload`) blueprint.
Social media dataset upload page.
"""
from app.models import User, Dataset, SMPost, SMReply
from bs4 import BeautifulSoup
import os
import pytest


@pytest.mark.order(6)
def test_upload_sm_login_required(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload_sm' page is requested (GET) without being logged in
    THEN check the response is valid and the user is redirected to the login page
    """
    response = test_client.get("/upload/upload_sm")
    assert response.status_code == 302  # check redirect
    assert "/auth/login" in response.headers["Location"]


def test_upload_sm_valid_login(test_client, insert_users):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload_sm' page is requested (GET) after logging in
    THEN check the response is valid
    """
    # log in to the app
    response = test_client.post(
        "/auth/login",
        data={"username": "admin1", "password": "admin1password"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # check upload page
    response = test_client.get("/upload/upload_sm")
    assert response.status_code == 200
    assert b"Upload new social media dataset" in response.data
    assert b"Dataset name" in response.data
    assert b"description" in response.data
    assert b'type="submit"' in response.data  # check submit button
    assert b'type="file"' in response.data  # check file upload button

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


def test_upload_sm_valid_dataset(test_client, insert_users):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload_sm' page is requested (POST) with a valid dataset (with one annotator)
    THEN check the response is valid and the dataset is added to the database correctly
    """
    # log in to the app
    response = test_client.post(
        "/auth/login",
        data={"username": "admin1", "password": "admin1password"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # check upload page
    response = test_client.get("/upload/upload_sm")
    assert response.status_code == 200

    path = test_client.application.config["SM_DATASET_PATH"]
    # upload a valid dataset
    with open(path, "rb") as handle:
        response = test_client.post(
            "/upload/upload_sm",
            data={
                "name": "test_dataset",
                "description": "test description",
                "annotators": User.query.filter_by(username="admin1").first().id,
                "file": (
                    handle,
                    os.path.basename(path),
                ),
            },
            follow_redirects=True,
        )
    assert response.status_code == 200
    assert b"File uploaded successfully" in response.data

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200

    # check dataset is uploaded correctly to the database
    dataset = Dataset.query.filter_by(name="test_dataset").first()
    user = User.query.filter_by(username="admin1").first()

    assert dataset
    assert dataset.name == "test_dataset"
    assert dataset.description == "test description"
    assert dataset.id_author == user.id
    assert dataset.annotators.all()[0].id == user.id
    assert dataset.type.value == "Social Media Thread"

    posts = SMPost.query.filter_by(id_dataset=dataset.id).all()
    assert posts
    assert posts[0].id_dataset == dataset.id
    replies = SMReply.query.filter_by(id_dataset=dataset.id).all()
    assert replies
    assert replies[0].id_dataset == dataset.id


def test_upload_sm_invalid_dataset(test_client, insert_users):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload_sm' page is requested (POST) with an invalid dataset
    THEN check a HTTP 400 error is raised with a helpful error message, and
    the dataset is not added to the database
    """
    # log in to the app
    response = test_client.post(
        "/auth/login",
        data={"username": "admin1", "password": "admin1password"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # check upload page
    response = test_client.get("/upload/upload_sm")
    assert response.status_code == 200

    path = test_client.application.config["PS_DATASET_PATH"]
    # upload an invalid dataset
    with open(path, "rb") as handle:
        response = test_client.post(
            "/upload/upload_sm",
            data={
                "name": "invalid_dataset",
                "description": "test description",
                "annotators": User.query.filter_by(username="admin1").first().id,
                "file": (
                    handle,
                    os.path.basename(path),
                ),
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
    WHEN the '/upload_sm' page is requested (GET) after logging in as a user with a role
    THEN check the 'Annotator' SelectField is populated with the correct users
    """
    # log in to the app as a user with the 'annotator' role
    response = test_client.post(
        "/auth/login",
        data={"username": "annotator1", "password": "annotator1password"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # check upload page
    response = test_client.get("/upload/upload_sm")
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
        data={"username": "admin1", "password": "admin1password"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # check upload page
    response = test_client.get("/upload/upload_sm")
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
