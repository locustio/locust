import pytest

pytest.importorskip("openai")


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "local-test-only")
    from locust.contrib.oai import OpenAIClient
    from locust.event import EventHook

    client = OpenAIClient(EventHook(), user=None)
    yield client
    client.close()


def test_nested_rename_request_restores_outer_name(client):
    with client.rename_request("outer"):
        with client.rename_request("inner"):
            assert client.request_name == "inner"
        assert client.request_name == "outer"
    assert client.request_name is None


def test_nested_rename_request_restores_outer_name_on_exception(client):
    with client.rename_request("outer"):
        with pytest.raises(ValueError):
            with client.rename_request("inner"):
                raise ValueError("boom")
        assert client.request_name == "outer"
    assert client.request_name is None


@pytest.mark.parametrize("raises", [False, True])
def test_rename_request_restores_existing_name(client, raises):
    client.request_name = "existing"
    try:
        with client.rename_request("temporary"):
            assert client.request_name == "temporary"
            if raises:
                raise ValueError("boom")
    except ValueError:
        pass
    assert client.request_name == "existing"
