"""
Functional tests for the main (`main`) blueprint.
"""


def test_home_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET) without logging in
    THEN check that the user is redirected to the login page
    """
    response = test_client.get("/")
    assert response.status_code == 302  # check redirect
    assert "/auth/login" in response.headers["Location"]


def test_home_page_logged_in(test_client, init_database_with_datasets):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET) after logging in
    THEN check that all datasets for that user are displayed
    """
    # Log in as annotator1
    response = test_client.post(
        "/auth/login",
        data={"username": "annotator1", "password": "annotator1password"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Check that the home page is displayed, and the expected datasets are displayed
    response = test_client.get("/")
    assert b"Hi, annotator1" in response.data
    assert b"Hi, admin1" not in response.data
    assert b"Social Media Dataset Test" in response.data
    assert b"Psychotherapy Dataset Test" in response.data
    assert b"test description for SM dataset" in response.data
    assert b"test description for psychotherapy dataset" in response.data
    assert b"Description" in response.data
    assert b"Type" in response.data
    assert b"Author" in response.data
    assert b"Created" in response.data

    # Log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200

    # Log in as admin1
    response = test_client.post(
        "/auth/login",
        data={"username": "admin1", "password": "admin1password"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Check that the home page is displayed, and the expected datasets are displayed
    response = test_client.get("/")
    assert b"Hi, admin1" in response.data
    assert b"Hi, annotator1" not in response.data
    assert b"Social Media Dataset Test" in response.data
    assert (
        b"Psychotherapy Dataset Test" not in response.data
    )  # admin1 is not an annotator for this dataset
    assert b"test description for psychotherapy dataset" not in response.data
    # Log out
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
