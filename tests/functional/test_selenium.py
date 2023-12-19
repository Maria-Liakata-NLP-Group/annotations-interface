import requests
import pytest
from selenium.webdriver.common.by import By


# NOTE: The following tests are dependent on the server running on localhost:5000.
#      To run these tests, run the server in a separate terminal window with
#     the following command: `flask run --host=localhost --port=5000`

# TODO: create a pytest fixture that starts the server and stops it after the tests are done


@pytest.mark.dependency()
def test_live_server():
    """Test that the server is running on localhost:5000."""
    try:
        response = requests.get("http://localhost:5000")
        assert response.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.fail("The server is not running on localhost:5000")


@pytest.mark.dependency(depends=["test_live_server"])
def test_login_page(driver):
    # NOTE: The following test assumes that the test_user has already been manually registered
    driver.get(
        "http://localhost:5000/index"
    )  # if not signed in, redirects to login page
    assert driver.title == "Sign In"
    driver.find_element(By.LINK_TEXT, "Login").click()
    assert driver.current_url == "http://localhost:5000/auth/login"
    assert driver.title == "Sign In"
    driver.find_element(By.ID, "username").send_keys("test_user")
    driver.find_element(By.ID, "password").send_keys("password")
    try:
        driver.find_element(By.ID, "submit").click()
        assert driver.current_url == "http://localhost:5000/index"
        assert driver.title == "Home page"
    except AssertionError:
        pytest.fail("Login failed. Have you registered the test_user?")


@pytest.mark.dependency(depends=["test_login_page"])
def test_home_page(driver):
    driver.get("http://localhost:5000/index")
    assert driver.title == "Home page"
    assert "Hi, test_user" in driver.page_source
    try:
        driver.find_element(By.LINK_TEXT, "Latin").click()
        assert (
            driver.current_url
            == "http://localhost:5000/annotate/annotate_psychotherapy/1"
        )
    except:
        pytest.fail(
            "Failed to navigate to the Latin psychotherapy dataset. Have you imported it?"
        )


@pytest.mark.dependency(depends=["test_home_page"])
def test_annotate_psychotherapy(driver):
    driver.get("http://localhost:5000/annotate/annotate_psychotherapy/1")
    assert driver.title == "Annotations Interface"
    assert "Page 1 of" in driver.page_source
    # check that the forms are initially collapsed
    assert driver.find_element(By.ID, "form_client").is_displayed() is False
    assert driver.find_element(By.ID, "form_therapist").is_displayed() is False
    assert driver.find_element(By.ID, "form_dyad").is_displayed() is False


@pytest.mark.dependency(depends=["test_annotate_psychotherapy"])
def test_annotate_client(driver):
    driver.get("http://localhost:5000/annotate/annotate_psychotherapy/1")
    # click on the client form button twice, as it was clicked once in the previous test
    driver.find_element(By.ID, "btn_client").click()
    driver.find_element(By.ID, "btn_client").click()
    # check that the client form is now visible
    assert driver.find_element(By.ID, "form_client").is_displayed
