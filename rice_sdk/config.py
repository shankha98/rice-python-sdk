import os
import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StorageConfig:
    enabled: bool = True


@dataclass
class StateConfig:
    enabled: bool = True
    llm_mode: bool = False
    flux_enabled: bool = False


@dataclass
class RiceConfig:
    storage: StorageConfig = field(default_factory=StorageConfig)
    state: StateConfig = field(default_factory=StateConfig)


def load_config(config_path: Optional[str] = None) -> RiceConfig:
    """
    Loads configuration from a JSON file or defaults.
    In the Python SDK, we prefer `rice.config.json` over `.js`.
    """
    default_path = os.path.abspath("rice.config.json")
    path = config_path if config_path else default_path

    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)

            storage_data = data.get("storage", {})
            state_data = data.get("state", {})

            storage_config = StorageConfig(enabled=storage_data.get("enabled", True))

            state_config = StateConfig(
                enabled=state_data.get("enabled", True),
                llm_mode=state_data.get("llm_mode", False),
                flux_enabled=state_data.get("flux", {}).get("enabled", False),
            )

            return RiceConfig(storage=storage_config, state=state_config)
        except Exception as e:
            raise RuntimeError(f"Failed to load config from {path}: {e}")

    return RiceConfig()
