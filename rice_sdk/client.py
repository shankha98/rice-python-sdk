import os
import sys
from typing import Optional, Dict, Any, Union
from dotenv import load_dotenv

from .config import load_config, RiceConfig
from .storage.client import RiceDBClient
from .state.client import StateClient


class Client:
    """
    Unified Client to access both Storage and State services.
    """

    def __init__(self, config_path: Optional[str] = None, run_id: Optional[str] = None):
        self.config_path = config_path
        self._options_run_id = run_id
        self._config: Optional[RiceConfig] = None
        self._storage: Optional[RiceDBClient] = None
        self._state: Optional[StateClient] = None

    def connect(self):
        # Load environment variables
        load_dotenv(os.path.join(os.getcwd(), ".env"))

        # Load config
        self._config = load_config(self.config_path)

        # Initialize Storage
        if self._config.storage.enabled:
            storage_url = (
                os.environ.get("STORAGE_INSTANCE_URL")
                or os.environ.get("RICEDB_HOST")
                or "localhost:50051"
            )

            host = "localhost"
            port = 50051

            parts = storage_url.split(":")
            if len(parts) == 2:
                host = parts[0]
                try:
                    port = int(parts[1])
                except ValueError:
                    pass
            else:
                host = storage_url

            token = os.environ.get("STORAGE_AUTH_TOKEN")
            user = os.environ.get("STORAGE_USER") or "admin"

            http_port_str = os.environ.get("STORAGE_HTTP_PORT")
            http_port = int(http_port_str) if http_port_str else 3000

            # Pass token to constructor initially
            self._storage = RiceDBClient(host, "auto", port, http_port, token)
            try:
                self._storage.connect()
            except Exception as e:
                # Log warning but continue? Node SDK does await connect() and fails if error?
                # Node SDK code: `await this._storage.connect();` so it throws if fails.
                # Here we should let it raise.
                raise e

            if token:
                try:
                    # Attempt auto-login using the token as password
                    # In Node SDK: `const newToken = await this._storage.login(user, token);`
                    self._storage.login(user, token)
                except Exception as e:
                    # Warn but don't crash
                    print(f"Auto-login failed for user {user}: {e}")

        # Initialize State
        if self._config.state.enabled:
            address = os.environ.get("STATE_INSTANCE_URL") or "localhost:50051"
            token = os.environ.get("STATE_AUTH_TOKEN")
            run_id = self._options_run_id or os.environ.get("STATE_RUN_ID") or "default"

            self._state = StateClient(address, token, run_id)
            # State client connects on first call typically in gRPC,
            # but we created the stub in __init__ which is fine.

    @property
    def storage(self) -> RiceDBClient:
        if not self._storage:
            raise RuntimeError(
                "Config mismatch: storage is not enabled or not connected"
            )
        return self._storage

    @property
    def state(self) -> StateClient:
        if not self._state:
            raise RuntimeError("Config mismatch: state is not enabled or not connected")
        return self._state
