import pytest
import json
from unittest.mock import MagicMock, patch
from rice_sdk.storage.client_grpc import GrpcClient
from rice_sdk.storage.proto import ricedb_pb2, ricedb_pb2_grpc


@pytest.fixture
def mock_grpc_channel():
    with patch("grpc.insecure_channel") as mock_channel:
        yield mock_channel


@pytest.fixture
def mock_ricedb_stub():
    with patch("rice_sdk.storage.client_grpc.ricedb_pb2_grpc.RiceDBStub") as mock_stub:
        yield mock_stub.return_value


def test_grpc_client_connect(mock_grpc_channel, mock_ricedb_stub):
    mock_ricedb_stub.Health.return_value = ricedb_pb2.HealthResponse(
        status="ok", version="1.0"
    )

    client = GrpcClient(host="localhost", port=50051)
    connected = client.connect()

    assert connected is True
    # Verify call arguments including options
    assert mock_grpc_channel.call_count == 1
    args, kwargs = mock_grpc_channel.call_args
    assert args[0] == "localhost:50051"
    assert "options" in kwargs
    mock_ricedb_stub.Health.assert_called_once()


def test_insert(mock_grpc_channel, mock_ricedb_stub):
    mock_ricedb_stub.Insert.return_value = ricedb_pb2.InsertResponse(
        success=True, nodeId=123
    )

    client = GrpcClient()
    client.connect()

    metadata = {"key": "value"}
    result = client.insert(123, "text", metadata)

    mock_ricedb_stub.Insert.assert_called_once()
    req = mock_ricedb_stub.Insert.call_args[0][0]
    assert req.id == 123
    assert req.text == "text"

    sent_meta = json.loads(req.metadata)
    assert sent_meta["key"] == "value"
    assert sent_meta["stored_text"] == "text"

    assert result["success"] is True


def test_search(mock_grpc_channel, mock_ricedb_stub):
    meta = json.dumps({"stored_text": "text"}).encode("utf-8")
    mock_ricedb_stub.Search.return_value = ricedb_pb2.SearchResponse(
        results=[ricedb_pb2.SearchResult(id=1, similarity=0.9, metadata=meta)]
    )

    client = GrpcClient()
    client.connect()

    results = client.search("query", user_id=1)

    mock_ricedb_stub.Search.assert_called_once()
    req = mock_ricedb_stub.Search.call_args[0][0]
    assert req.queryText == "query"

    assert len(results) == 1
    assert results[0]["id"] == 1
    assert results[0]["data"] == "text"
