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
    def test_fail_example_crit(self):
        var = 'crit_var'
        print(var)
        assert var == "error_variable"

    @pytest.mark.norm
    @pytest.mark.usefixtures('setup_class')
    def test_fail_example_norm(self):
        var = 'norm_var'
        print(var)
        assert var == "error_variable"

    @pytest.mark.crit
    @pytest.mark.usefixtures('setup_class', 'base_setup')
    def test_import_src(self):
        var = 'crit_non-app_data_var'
        id = AppData.return_config_data()
        print(var)
        assert var == id


