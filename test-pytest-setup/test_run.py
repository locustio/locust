import math
import pytest


class TestGroup():
    setup_data = ""

    @pytest.fixture
    def setup_class(self):
        self.setup_data = "setup_class_data"
        print("setup")

    def teardown_class(self):
        print("teardown")

    @pytest.mark.smoke
    @pytest.mark.usefixtures('setup_class')
    def test_setup_data(self):
        var = 'my_var_variable'
        print(var)
        assert var == self.setup_data

    @pytest.mark.smoke
    @pytest.mark.usefixtures('setup_class')
    def test_failure(self):
        var = 'my_var_variable'
        print(var)
        assert var == "mis_matched_value"

    @pytest.mark.usefixtures('setup_class')
    def test_math_root(self):
        print('sup')
        num = 35
        assert math.sqrt(num) == 5
