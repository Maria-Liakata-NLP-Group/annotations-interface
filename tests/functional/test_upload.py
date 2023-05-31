"""
Functional tests for the upload (`upload`) blueprint.
"""


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
        data={"username": "test1", "password": "testpassword1"},
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


def test_upload_sm_valid_dataset(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload_sm' page is requested (POST) with a valid dataset
    THEN check the response is valid and the dataset is added to the database
    """
    # log in to the app
    response = test_client.post(
        "/auth/login",
        data={"username": "test1", "password": "testpassword1"},
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
                "file": (handle, "timelines_example_lorem.pickle"),
            },
            follow_redirects=True,
        )
    assert response.status_code == 200
    assert b"File uploaded successfully" in response.data

    # check dataset is in database, and has correct number of posts and replies
    from app.models import User, Dataset, SMPost, SMReply

    dataset = Dataset.query.filter_by(name="test_dataset").first()
    user = User.query.filter_by(username="test1").first()

    assert dataset is not None
    assert dataset.name == "test_dataset"
    assert dataset.description == "test description"
    assert dataset.id_user == user.id

    posts = SMPost.query.filter_by(id_dataset=dataset.id).all()
    assert len(posts) == 43

    replies = SMReply.query.filter_by(id_dataset=dataset.id).all()
    assert len(replies) == 92
