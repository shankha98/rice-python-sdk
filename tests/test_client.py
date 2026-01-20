import pytest
from unittest.mock import patch
from rice_sdk.client import Client


@pytest.fixture
def mock_load_config():
    with patch("rice_sdk.client.load_config") as mock:
        mock.return_value.storage.enabled = True
        mock.return_value.state.enabled = True
        yield mock


@pytest.fixture
def mock_storage_client():
    with patch("rice_sdk.client.RiceDBClient") as mock:
        yield mock


@pytest.fixture
def mock_state_client():
    with patch("rice_sdk.client.StateClient") as mock:
        yield mock


def test_client_init(mock_load_config, mock_storage_client, mock_state_client):
    with patch.dict(
        "os.environ",
        {
            "STORAGE_INSTANCE_URL": "localhost:50051",
            "STATE_INSTANCE_URL": "localhost:50051",
        },
    ):
        client = Client()
        client.connect()

        assert client.storage is not None
        assert client.state is not None

        mock_storage_client.assert_called_once()
        mock_state_client.assert_called_once()


def test_client_init_disabled_storage(
    mock_load_config, mock_storage_client, mock_state_client
):
    mock_load_config.return_value.storage.enabled = False

    client = Client()
    client.connect()

    with pytest.raises(RuntimeError, match="storage is not enabled"):
        _ = client.storage

    assert client.state is not None
