import pytest
import requests


# see https://pytest-flask.readthedocs.io/en/latest/features.html#live-server-application-live-server
@pytest.mark.usefixtures("live_server")
class TestLiveServer:
    def test_server_is_up_and_running(self):
        res = requests.get("http://127.0.0.1:5000")
        res.status_code == 200

    def test_selenium(self, driver):
        driver.get("http://127.0.0.1:5000")
        assert driver.title == "Annotations Interface"
