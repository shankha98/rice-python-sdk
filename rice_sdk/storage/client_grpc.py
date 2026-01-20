import grpc
import json
from typing import Optional, List, Dict, Any, Union
from .proto import ricedb_pb2, ricedb_pb2_grpc
from .utils import to_long


class GrpcClient:
    def __init__(
        self, host: str = "localhost", port: int = 50051, token: Optional[str] = None
    ):
        self.host = host
        self.port = port
        self.token = token
        self.client = None
        self.channel = None
        self.connected = False

    def connect(self) -> bool:
        address = f"{self.host}:{self.port}"
        self.channel = grpc.insecure_channel(
            address,
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )
        self.client = ricedb_pb2_grpc.RiceDBStub(self.channel)

        try:
            self.health()
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            raise e

    def disconnect(self):
        if self.channel:
            self.channel.close()
        self.client = None
        self.connected = False

    def _get_metadata(self):
        metadata = []
        if self.token:
            metadata.append(("authorization", f"Bearer {self.token}"))
        return metadata

    def health(self) -> Dict[str, str]:
        if not self.client:
            raise RuntimeError("Not connected")
        res = self.client.Health(
            ricedb_pb2.HealthRequest(), metadata=self._get_metadata()
        )
        return {"status": res.status, "version": res.version}

    def insert(
        self,
        node_id: Union[int, str],
        text: str,
        metadata: Dict[str, Any],
        user_id: Union[int, str] = 1,
        session_id: Optional[str] = None,
        embedding: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("Not connected")

        # Automatically store text in metadata so it can be retrieved
        meta = metadata.copy()
        if text and "stored_text" not in meta:
            meta["stored_text"] = text

        req = ricedb_pb2.InsertRequest(
            id=to_long(node_id),
            text=text,
            metadata=json.dumps(meta).encode("utf-8"),
            userId=to_long(user_id),
            sessionId=session_id,
            embedding=embedding or [],
        )

        res = self.client.Insert(req, metadata=self._get_metadata())
        return {"success": res.success, "nodeId": res.nodeId, "message": res.message}

    def search(
        self,
        query: str,
        user_id: Union[int, str] = 1,
        k: int = 10,
        session_id: Optional[str] = None,
        filter_dict: Optional[Dict[str, Any]] = None,
        query_embedding: Optional[List[float]] = None,
    ) -> List[Dict[str, Any]]:
        if not self.client:
            raise RuntimeError("Not connected")

        req = ricedb_pb2.SearchRequest(
            queryText=query,
            userId=to_long(user_id),
            k=k,
            sessionId=session_id,
            filter=json.dumps(filter_dict) if filter_dict else "",
            queryEmbedding=query_embedding or [],
        )

        res = self.client.Search(req, metadata=self._get_metadata())
        results = []
        for r in res.results:
            try:
                meta = json.loads(r.metadata)
            except:
                meta = {}
            results.append(
                {
                    "id": r.id,
                    "similarity": r.similarity,
                    "metadata": meta,
                    "data": meta.get("stored_text"),
                }
            )
        return results

    def delete(
        self, node_id: Union[int, str], session_id: Optional[str] = None
    ) -> bool:
        if not self.client:
            raise RuntimeError("Not connected")
        res = self.client.DeleteNode(
            ricedb_pb2.DeleteNodeRequest(nodeId=to_long(node_id), sessionId=session_id),
            metadata=self._get_metadata(),
        )
        return res.success

    def login(self, username: str, password: str) -> str:
        if not self.client:
            raise RuntimeError("Not connected")
        res = self.client.Login(
            ricedb_pb2.LoginRequest(username=username, password=password),
            metadata=self._get_metadata(),
        )
        self.token = res.token
        return res.token
