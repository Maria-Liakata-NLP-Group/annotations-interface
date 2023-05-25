"""
Functional tests for the authentication (`auth`) blueprint.
"""


def test_login_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get("/auth/login")
    assert response.status_code == 200
    assert b"Sign In" in response.data
    assert b"Username" in response.data
    assert b"Password" in response.data
    assert b"Remember Me" in response.data
    assert b"New User?" in response.data
    assert b"Click to Register" in response.data


def test_valid_login_logout(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST) with valid credentials
    THEN check the response is valid and the user is redirected to the home page
    """
    response = test_client.post(
        "/auth/login",
        data={"username": "test1", "password": "testpassword1"},
        follow_redirects=True,
    )  # redirects to home page
    assert response.status_code == 200
    assert b"Logout" in response.data
    assert b"test1" in response.data
    assert b"New User?" not in response.data
    assert b"Click to Register" not in response.data
    assert b"Sign In" not in response.data

    """
    GIVEN a Flask application configured for testing
    WHEN the '/logout' page is requested (GET)
    THEN check the response is valid and the user is redirected to the login page
    """
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign In" in response.data
    assert b"test1" not in response.data


def test_invalid_login(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST) with invalid credentials
    THEN check an error message is returned to the user and they are prompted to try again
    """
    response = test_client.post(
        "auth/login",
        data={"username": "test1", "password": "wrongpassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data
    assert b"Sign In" in response.data
    assert b"test1" not in response.data
    assert b"New User?" in response.data
    assert b"Click to Register" in response.data


def test_valid_registration(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST) with a registered username
    THEN check an error message is returned to the user and they are prompted to try again
    """
    response = test_client.post(
        "/auth/register",
        data={
            "username": "test1",
            "email": "test1@example.com",
            "email2": "test1@example.com",
            "password": "testpassword1",
            "password2": "testpassword1",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Username already exists. Please use a different username." in response.data
    assert b"Register" in response.data

    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST) with a new username
    THEN check the user is redirected to the login page
    """
    response = test_client.post(
        "/auth/register",
        data={
            "username": "test3",
            "email": "test3@example.com",
            "email2": "test3@example.com",
            "password": "testpassword3",
            "password2": "testpassword3",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"You have successfully registered!" in response.data
    assert b"Sign In" in response.data
