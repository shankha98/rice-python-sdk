import requests
import json
from typing import Optional, List, Dict, Any, Union
from .utils import to_long


class HttpClient:
    def __init__(
        self, host: str = "localhost", port: int = 3000, token: Optional[str] = None
    ):
        self.host = host
        self.port = port
        self.token = token
        self.base_url = f"http://{host}:{port}"
        self.connected = False

    def connect(self) -> bool:
        try:
            self.health()
            self.connected = True
            return True
        except Exception:
            self.connected = False
            raise

    def disconnect(self):
        self.connected = False

    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def health(self) -> Dict[str, str]:
        resp = requests.get(f"{self.base_url}/health", headers=self._get_headers())
        resp.raise_for_status()
        return resp.json()

    def insert(
        self,
        node_id: Union[int, str],
        text: str,
        metadata: Dict[str, Any],
        user_id: Union[int, str] = 1,
        session_id: Optional[str] = None,
        embedding: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        if not self.connected:
            raise RuntimeError("Not connected")

        # Automatically store text in metadata
        meta = metadata.copy()
        if text and "stored_text" not in meta:
            meta["stored_text"] = text

        payload = {
            "id": to_long(node_id),
            "text": text,
            "metadata": meta,
            "user_id": to_long(user_id),
            "embedding": embedding or [],
        }
        if session_id:
            payload["session_id"] = session_id

        resp = requests.post(
            f"{self.base_url}/v1/nodes", json=payload, headers=self._get_headers()
        )
        resp.raise_for_status()

        data = resp.json()
        # Normalize response to match GRPC output structure if possible, or keep as raw
        # Node SDK makes them consistent.
        return {
            "success": data.get("success", True),
            "nodeId": data.get("node_id"),
            "message": data.get("message", ""),
        }

    def search(
        self,
        query: str,
        user_id: Union[int, str] = 1,
        k: int = 10,
        session_id: Optional[str] = None,
        filter_dict: Optional[Dict[str, Any]] = None,
        query_embedding: Optional[List[float]] = None,
    ) -> List[Dict[str, Any]]:
        if not self.connected:
            raise RuntimeError("Not connected")

        payload = {
            "query": query,
            "user_id": to_long(user_id),
            "k": k,
            "query_embedding": query_embedding or [],
        }
        if session_id:
            payload["session_id"] = session_id
        if filter_dict:
            payload["filter"] = filter_dict

        resp = requests.post(
            f"{self.base_url}/v1/search", json=payload, headers=self._get_headers()
        )
        resp.raise_for_status()

        data = resp.json()
        results = []
        for r in data.get("results", []):
            results.append(
                {
                    "id": r.get("id"),
                    "similarity": r.get("similarity"),
                    "metadata": r.get("metadata", {}),
                    "data": r.get("metadata", {}).get("stored_text"),
                }
            )
        return results

    def delete(
        self, node_id: Union[int, str], session_id: Optional[str] = None
    ) -> bool:
        if not self.connected:
            raise RuntimeError("Not connected")

        url = f"{self.base_url}/v1/nodes/{to_long(node_id)}"
        params = {}
        if session_id:
            params["session_id"] = session_id

        resp = requests.delete(url, params=params, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json().get("success", True)

    def login(self, username: str, password: str) -> str:
        resp = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password},
        )
        resp.raise_for_status()
        data = resp.json()
        self.token = data.get("token")
        return self.token
