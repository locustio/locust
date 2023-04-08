import pytest
import requests
from bs4 import BeautifulSoup
import pytest_check as check

class TestGroup():
    setup_data = ""

    @pytest.fixture
    def setup_class(self):
        self.setup_data = "setup_class_data"
        print("**Setup**")

    def teardown_class(self):
        print("**Teardown**")

    @pytest.mark.smoke
    @pytest.mark.usefixtures('setup_class')
    def test_requests_url(self):
        url = 'https://en.wikipedia.org/wiki/Wiki'
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        class_name = 'mw-page-title-main'
        element_type = 'span'
        web_element = soup.find(element_type, {"class": class_name})
        actual_text = web_element.get_text()
        expected_text = 'Wiki'
        wrong_text = 'Cheese'
        #check.equal(actual_text, wrong_text, "the same (but here it is an error)")
        check.equal(actual_text, expected_text, "the same")
