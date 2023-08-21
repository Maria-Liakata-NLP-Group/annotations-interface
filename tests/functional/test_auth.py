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


def test_valid_login_logout(test_client, insert_users):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST) with valid credentials
    THEN check the response is valid and the user is redirected to the home page
    """
    response = test_client.post(
        "/auth/login",
        data={"username": "admin1", "password": "admin1password"},
        follow_redirects=True,
    )  # redirects to home page
    assert response.status_code == 200
    assert b"Logout" in response.data
    assert b"Hi, admin1" in response.data
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
    assert b"admin1" not in response.data


def test_invalid_login(test_client, insert_users):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST) with invalid credentials
    THEN check an error message is returned to the user and they are prompted to try again
    """
    response = test_client.post(
        "auth/login",
        data={"username": "admin1", "password": "wrongpassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data
    assert b"Sign In" in response.data
    assert b"admin1" not in response.data
    assert b"New User?" in response.data
    assert b"Click to Register" in response.data


def test_valid_registration(test_client, insert_users):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST) with a registered username
    THEN check an error message is returned to the user and they are prompted to try again
    """
    response = test_client.post(
        "/auth/register",
        data={
            "username": "admin1",
            "email": "admin1@example.com",
            "email2": "admin1@example.com",
            "password": "admin1password",
            "password2": "admin1password",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Username already exists. Please use a different username." in response.data
    # check that the url is still /register
    assert response.request.path == "/auth/register"

    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST) with a registered email address
    THEN check an error message is returned to the user and they are prompted to try again
    """
    response = test_client.post(
        "/auth/register",
        data={
            "username": "test",
            "email": "admin1@example.com",
            "email2": "admin1@example.com",
            "password": "testpassword",
            "password2": "testpassword",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Email already exists. Please use a different email." in response.data
    # check that the url is still /register
    assert response.request.path == "/auth/register"

    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST) with a new username
    THEN check the user is redirected to the login page
    """
    response = test_client.post(
        "/auth/register",
        data={
            "username": "annotator2",
            "email": "annotator2@example.com",
            "email2": "annotator2@example.com",
            "password": "annotatorpassword2",
            "password2": "annotatorpassword2",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"You have successfully registered!" in response.data
    assert b"Sign In" in response.data


def test_correct_role_assignment(test_client, insert_users):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST) with a new username
    THEN check the user is assigned the correct role
    """
    # Create a new user with the role "Annotator"
    response = test_client.post(
        "/auth/register",
        data={
            "username": "annotator3",
            "email": "annotator3@example.com",
            "email2": "annotator3@example.com",
            "password": "annotatorpassword3",
            "password2": "annotatorpassword3",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"You have successfully registered!" in response.data

    # Create a new user with the role "Administrator",
    # identified by the email address specified in the config file
    response = test_client.post(
        "/auth/register",
        data={
            "username": "admin2",
            "email": "admin2@example.com",
            "email2": "admin2@example.com",
            "password": "adminpassword2",
            "password2": "adminpassword2",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"You have successfully registered!" in response.data

    from app.models import User, Role

    role = Role.query.filter_by(name="Annotator").first()
    user = User.query.filter_by(username="annotator3").first()
    assert user.id_role == role.id

    role = Role.query.filter_by(name="Administrator").first()
    user = User.query.filter_by(username="admin2").first()
    assert user.id_role == role.id
