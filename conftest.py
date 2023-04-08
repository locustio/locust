import pytest
import sys

@pytest.fixture(scope='class', name='base_setup')
def base_setup():
    print('**base setup**')
    return "return statement"


@pytest.fixture(scope='function', autouse=True)
def update_log_on_teardown():
    yield
    print('new message on teardown')
