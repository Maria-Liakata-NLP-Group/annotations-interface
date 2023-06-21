"""
Functional tests for the upload (`upload`) blueprint.
"""
from app.models import User, Dataset, SMPost, SMReply
from bs4 import BeautifulSoup


def test_upload_sm_login_required(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload_sm' page is requested (GET) without being logged in
    THEN check the response is valid and the user is redirected to the login page
    """
    response = test_client.get("/upload/upload_sm")
    assert response.status_code == 302  # check redirect
    assert "/auth/login" in response.headers["Location"]


def test_upload_sm_valid_login(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload_sm' page is requested (GET) after logging in
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
    response = test_client.get("/upload/upload_sm")
    assert response.status_code == 200
    assert b"Upload new dataset" in response.data
    assert b"Dataset name" in response.data
    assert b"description" in response.data
    assert b'type="submit"' in response.data  # check submit button
    assert b'type="file"' in response.data  # check file upload button

    # log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


def test_upload_sm_valid_dataset(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload_sm' page is requested (POST) with a valid dataset
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
    response = test_client.get("/upload/upload_sm")
    assert response.status_code == 200

    # upload a valid dataset
    with open("tests/data/timelines_example_lorem.pickle", "rb") as handle:
        response = test_client.post(
            "/upload/upload_sm",
            data={
                "name": "test_dataset",
                "description": "test description",
                "annotator": User.query.filter_by(username="admin1").first().id,
                "file": (handle, "timelines_example_lorem.pickle"),
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
    user = User.query.filter_by(username="admin1").first()

    assert dataset is not None
    assert dataset.name == "test_dataset"
    assert dataset.description == "test description"
    assert dataset.id_author == user.id

    posts = SMPost.query.filter_by(id_dataset=dataset.id).all()
    assert len(posts) == 43
    replies = SMReply.query.filter_by(id_dataset=dataset.id).all()
    assert len(replies) == 92

    # more granular checks
    posts = SMPost.query.filter_by(
        user_id="746731", timeline_id="746731_1", id_dataset=dataset.id
    ).all()
    assert len(posts) == 10

    post = SMPost.query.filter_by(
        user_id="746731", timeline_id="746731_1", post_id=9602529, id_dataset=dataset.id
    ).first()
    assert (post.mood).lower() == "happy"
    replies = SMReply.query.filter_by(id_sm_post=post.id).all()
    assert len(replies) == 2


def test_upload_based_on_role(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload_sm' page is requested (GET) after logging in as a user with a role
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
    response = test_client.get("/upload/upload_sm")
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")  # parse HTML
    select_element = soup.find(
        "select", id="annotator"
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
    response = test_client.get("/upload/upload_sm")
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")  # parse HTML
    select_element = soup.find(
        "select", id="annotator"
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
