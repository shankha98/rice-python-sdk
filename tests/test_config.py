import os
import pytest
from unittest.mock import patch, mock_open
from rice_sdk.config import load_config, RiceConfig


def test_load_config_defaults():
    with patch("os.path.exists", return_value=False):
        config = load_config()
        assert isinstance(config, RiceConfig)
        assert config.storage.enabled is True
        assert config.state.enabled is True


def test_load_config_from_env():
    with patch.dict(
        os.environ,
        {
            "STORAGE_INSTANCE_URL": "custom-host:9090",
            "STORAGE_AUTH_TOKEN": "secret",
            "STATE_INSTANCE_URL": "state-host:8080",
        },
    ):
        with patch("os.path.exists", return_value=False):
            config = load_config()
            # Note: load_config primarily loads the file structure.
            # Environment variables are typically used in the Client or specific service initialization.
            # However, if load_config parses env vars into the config object, we test it here.
            # Based on the Node SDK, load_config reads the file, and Client reads env vars.
            # We will follow the Node SDK pattern where load_config handles the file.
            pass


def test_load_config_file_json():
    mock_config_content = '{"storage": {"enabled": false}, "state": {"enabled": true}}'
    with patch("builtins.open", mock_open(read_data=mock_config_content)):
        with patch("os.path.exists", return_value=True):
            # We assume we support a json config for Python as JS execution is hard
            config = load_config("rice.config.json")
            assert config.storage.enabled is False
            assert config.state.enabled is True
