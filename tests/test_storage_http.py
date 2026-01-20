import pytest
import json
from unittest.mock import MagicMock, patch
from rice_sdk.storage.client_http import HttpClient


def test_http_client_connect():
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "ok", "version": "1.0"}

        client = HttpClient(host="localhost", port=3000)
        connected = client.connect()

        assert connected is True
        args, kwargs = mock_get.call_args
        assert args[0] == "http://localhost:3000/health"
        assert kwargs["headers"] == {"Content-Type": "application/json"}


def test_insert_http():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "success": True,
            "node_id": 123,
            "message": "ok",
        }

        client = HttpClient()
        client.connected = True

        metadata = {"key": "value"}
        result = client.insert(123, "text", metadata)

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "http://localhost:3000/v1/nodes"

        data = kwargs["json"]
        assert data["id"] == 123
        assert data["text"] == "text"
        assert data["metadata"]["key"] == "value"

        assert result["success"] is True


def test_search_http():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "results": [
                {"id": 1, "similarity": 0.9, "metadata": {"stored_text": "text"}}
            ]
        }

        client = HttpClient()
        client.connected = True

        results = client.search("query", user_id=1)

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "http://localhost:3000/v1/search"

        data = kwargs["json"]
        assert data["query"] == "query"
        assert data["user_id"] == 1

        assert len(results) == 1
        assert results[0]["data"] == "text"
