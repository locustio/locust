import unittest
from unittest.mock import patch

import pytest

pytest.importorskip("psycopg")

from locust.contrib import postgres


class TestPostgresClient(unittest.TestCase):
    def test_connection_is_in_autocommit_mode(self):
        with patch.object(postgres.psycopg, "connect") as connect:
            postgres.PostgresClient("postgresql://localhost/my_db")

        connect.assert_called_once_with("postgresql://localhost/my_db", autocommit=True)
