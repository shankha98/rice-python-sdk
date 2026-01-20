from typing import Union, Optional, List, Dict, Any
from .client_grpc import GrpcClient
from .client_http import HttpClient


class RiceDBClient:
    """
    Client for RiceDB (Persistent Semantic Database).
    Supports both gRPC and HTTP transports.
    """

    def __init__(
        self,
        host: str = "localhost",
        transport: str = "auto",
        grpc_port: int = 50051,
        http_port: int = 3000,
        token: Optional[str] = None,
    ):
        self.host = host
        self.transport = transport
        self.grpc_port = grpc_port
        self.http_port = http_port
        self.token = token
        self.client: Union[GrpcClient, HttpClient, None] = None
        self.connected = False

    def connect(self) -> bool:
        if self.transport == "grpc":
            self.client = GrpcClient(self.host, self.grpc_port, self.token)
            self.connected = self.client.connect()
            return self.connected
        elif self.transport == "http":
            self.client = HttpClient(self.host, self.http_port, self.token)
            self.connected = self.client.connect()
            return self.connected
        else:  # auto
            try:
                self.client = GrpcClient(self.host, self.grpc_port, self.token)
                self.connected = self.client.connect()
                return self.connected
            except Exception as e:
                # Fallback to HTTP
                self.client = HttpClient(self.host, self.http_port, self.token)
                self.connected = self.client.connect()
                return self.connected

    def disconnect(self):
        if self.client:
            self.client.disconnect()
            self.client = None
        self.connected = False

    def _check_connected(self):
        if not self.client or not self.connected:
            raise RuntimeError("Not connected")

    def health(self) -> Dict[str, str]:
        self._check_connected()
        return self.client.health()

    def insert(
        self,
        node_id: Union[int, str],
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Union[int, str] = 1,
        session_id: Optional[str] = None,
        embedding: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        self._check_connected()
        return self.client.insert(
            node_id, text, metadata or {}, user_id, session_id, embedding
        )

    def batch_insert(
        self, items: List[Dict[str, Any]], user_id: Union[int, str] = 1
    ) -> Dict[str, Any]:
        """
        Batch insert items.
        Items should be a list of dicts with: nodeId, text, metadata, embedding (optional).
        """
        self._check_connected()
        success_count = 0
        errors = []
        for item in items:
            try:
                self.client.insert(
                    item["nodeId"],
                    item["text"],
                    item.get("metadata", {}),
                    user_id,
                    item.get("sessionId"),
                    item.get("embedding"),
                )
                success_count += 1
            except Exception as e:
                errors.append(str(e))

        return {"totalInserted": success_count, "failed": len(errors), "errors": errors}

    def search(
        self,
        query: str,
        user_id: Union[int, str] = 1,
        k: int = 10,
        session_id: Optional[str] = None,
        filter_dict: Optional[Dict[str, Any]] = None,
        query_embedding: Optional[List[float]] = None,
    ) -> List[Dict[str, Any]]:
        self._check_connected()
        return self.client.search(
            query, user_id, k, session_id, filter_dict, query_embedding
        )

    def delete(
        self, node_id: Union[int, str], session_id: Optional[str] = None
    ) -> bool:
        self._check_connected()
        return self.client.delete(node_id, session_id)

    def login(self, username: str, password: str) -> str:
        self._check_connected()
        token = self.client.login(username, password)
        self.token = token
        return token
