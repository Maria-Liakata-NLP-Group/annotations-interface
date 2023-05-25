"""
Functional tests for the main (`main`) blueprint.
"""


def test_home_page(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET) without logging in
    THEN check that the user is redirected to the login page
    """
    response = test_client.get("/")
    assert response.status_code == 302  # check redirect
    assert "/auth/login" in response.headers["Location"]
