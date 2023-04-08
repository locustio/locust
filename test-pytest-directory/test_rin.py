import pytest
from app_data import AppData


class TestGroup():
    setup_data = ""

    @pytest.fixture
    def setup_class(self):
        self.setup_data = "setup_data_var"
        print("setup")

    def teardown_class(self):
        print("teardown")

    @pytest.mark.crit
    @pytest.mark.usefixtures('setup_class')
    def test_third(self):
        var = 'my_var_variable'
        print(var)
        assert var == "quack"

    @pytest.mark.crit
    @pytest.mark.usefixtures('setup_class')
    def test_sixth(self):
        var = 'my_var_variable'
        id = AppData.return_message('quack')
        print(var)
        assert var == id

