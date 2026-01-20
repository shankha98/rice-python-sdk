import pytest
from unittest.mock import MagicMock
from rice_sdk.tools.execute import execute
from rice_sdk.state.client import StateClient


@pytest.mark.asyncio
async def test_execute_tool():
    mock_state_client = MagicMock(spec=StateClient)

    # Test focus
    await execute("focus", {"content": "test"}, mock_state_client)
    mock_state_client.focus.assert_called_with("test")

    # Test recall
    await execute("recall", {"query": "test"}, mock_state_client)
    mock_state_client.reminisce.assert_called_with("test")

    # Test setVariable
    await execute("setVariable", {"name": "var", "value": 1}, mock_state_client)
    mock_state_client.set_variable.assert_called_with("var", 1, "explicit")
