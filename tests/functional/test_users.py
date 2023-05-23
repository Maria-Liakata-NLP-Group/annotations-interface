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
    THEN check the response is valid
    """
    response = test_client.post(
        "/auth/login",
        data={"username": "test1", "password": "testpassword1"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Logout" in response.data
    assert b"test1" in response.data
    assert b"New User?" not in response.data
    assert b"Click to Register" not in response.data
    assert b"Sign In" not in response.data

    """
    GIVEN a Flask application configured for testing
    WHEN the '/logout' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign In" in response.data
    assert b"test1" not in response.data


def test_invalid_login(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST) with invalid credentials
    THEN check an error message is returned to the user
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
