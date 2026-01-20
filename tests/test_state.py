import pytest
from unittest.mock import MagicMock, patch
from rice_sdk.state.client import StateClient
from rice_sdk.state.proto import state_pb2, state_pb2_grpc


@pytest.fixture
def mock_grpc_channel():
    with patch("grpc.insecure_channel") as mock_channel:
        yield mock_channel


@pytest.fixture
def mock_cortex_stub():
    with patch("rice_sdk.state.client.state_pb2_grpc.CortexStub") as mock_stub:
        yield mock_stub.return_value


def test_state_client_init(mock_grpc_channel, mock_cortex_stub):
    client = StateClient(address="localhost:50051", token="my-token", run_id="test-run")
    mock_grpc_channel.assert_called_once_with("localhost:50051")
    # Verify authentication metadata is stored
    assert client.metadata == [("authorization", "my-token")]
    assert client.run_id == "test-run"


def test_focus(mock_grpc_channel, mock_cortex_stub):
    mock_cortex_stub.Focus.return_value = state_pb2.FocusResponse(id="focus-123")

    client = StateClient(run_id="test-run")
    response = client.focus("Task Context")

    mock_cortex_stub.Focus.assert_called_once()
    call_args = mock_cortex_stub.Focus.call_args[0][0]
    assert call_args.content == "Task Context"
    assert call_args.run_id == "test-run"
    assert response == "focus-123"


def test_drift(mock_grpc_channel, mock_cortex_stub):
    mock_cortex_stub.Drift.return_value = state_pb2.DriftResponse(
        items=[state_pb2.FluxItem(id="1", content="item1", relevance=0.9)]
    )

    client = StateClient(run_id="test-run")
    items = client.drift()

    mock_cortex_stub.Drift.assert_called_once()
    assert len(items) == 1
    assert items[0].content == "item1"


def test_commit(mock_grpc_channel, mock_cortex_stub):
    mock_cortex_stub.Commit.return_value = state_pb2.Ack(success=True)

    client = StateClient(run_id="test-run")
    success = client.commit("Input", "Output", action="test_action")

    mock_cortex_stub.Commit.assert_called_once()
    trace = mock_cortex_stub.Commit.call_args[0][0]
    assert trace.input == "Input"
    assert trace.outcome == "Output"
    assert trace.action == "test_action"
    assert trace.run_id == "test-run"
    assert success is True


def test_reminisce(mock_grpc_channel, mock_cortex_stub):
    mock_cortex_stub.Reminisce.return_value = state_pb2.RecallResponse(
        traces=[state_pb2.Trace(input="old input", outcome="old output")]
    )

    client = StateClient(run_id="test-run")
    memories = client.reminisce("query", limit=5)

    mock_cortex_stub.Reminisce.assert_called_once()
    req = mock_cortex_stub.Reminisce.call_args[0][0]
    assert req.query_text == "query"
    assert req.limit == 5
    assert req.run_id == "test-run"
    assert len(memories) == 1
    assert memories[0].input == "old input"
