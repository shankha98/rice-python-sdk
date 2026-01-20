import grpc
import json
from typing import List, Optional, Any, Dict
from .proto import state_pb2, state_pb2_grpc


class StateClient:
    """
    Client for interacting with State (AI Memory).
    Provides methods for managing conversational memory, drift, and skills.
    """

    def __init__(
        self,
        address: str = "localhost:50051",
        token: Optional[str] = None,
        run_id: str = "default",
    ):
        self.channel = grpc.insecure_channel(address)
        self.client = state_pb2_grpc.CortexStub(self.channel)
        self.metadata = []
        if token:
            self.metadata.append(("authorization", token))
        self.run_id = run_id

    def focus(self, content: str) -> str:
        """Stores a piece of information in short-term working memory (Flux)."""
        request = state_pb2.FocusRequest(content=content, run_id=self.run_id)
        response = self.client.Focus(request, metadata=self.metadata)
        return response.id

    def drift(self) -> List[Any]:
        """Reads current items from short-term memory."""
        request = state_pb2.DriftRequest(run_id=self.run_id)
        response = self.client.Drift(request, metadata=self.metadata)
        return list(response.items)

    def commit(
        self,
        input_text: str,
        output: str,
        action: str = "",
        agent_id: str = "",
        embedding: List[float] = None,
    ) -> bool:
        """Stores information in long-term persistent memory (Echoes)."""
        trace = state_pb2.Trace(
            input=input_text,
            outcome=output,
            action=action,
            agent_id=agent_id,
            embedding=embedding or [],
            run_id=self.run_id,
        )
        # Note: Node SDK takes 'options' object for action/agent_id. Python uses named args.
        response = self.client.Commit(trace, metadata=self.metadata)
        return response.success

    def reminisce(self, query: str, limit: int = 5, filter_str: str = "") -> List[Any]:
        """Recalls relevant memories from long-term memory."""
        request = state_pb2.RecallRequest(
            query_text=query, limit=limit, filter=filter_str, run_id=self.run_id
        )
        response = self.client.Reminisce(request, metadata=self.metadata)
        return list(response.traces)

    def set_variable(self, name: str, value: Any, source: str = "explicit") -> bool:
        """Sets a structured variable in working memory."""
        value_json = json.dumps(value)
        request = state_pb2.SetVariableRequest(
            run_id=self.run_id, name=name, value_json=value_json, source=source
        )
        response = self.client.SetVariable(request, metadata=self.metadata)
        return response.success

    def get_variable(self, name: str) -> Dict[str, Any]:
        """Gets a structured variable from working memory."""
        request = state_pb2.GetVariableRequest(run_id=self.run_id, name=name)
        response = self.client.GetVariable(request, metadata=self.metadata)
        return {
            "name": response.name,
            "value": json.loads(response.value_json),
            "source": response.source,
        }

    def list_variables(self) -> List[Dict[str, Any]]:
        """Lists all variables in working memory."""
        request = state_pb2.ListVariablesRequest(run_id=self.run_id)
        response = self.client.ListVariables(request, metadata=self.metadata)
        return [
            {"name": v.name, "value": json.loads(v.value_json), "source": v.source}
            for v in response.variables
        ]

    def delete_variable(self, name: str) -> bool:
        """Deletes a variable from working memory."""
        request = state_pb2.DeleteVariableRequest(run_id=self.run_id, name=name)
        response = self.client.DeleteVariable(request, metadata=self.metadata)
        return response.success

    def set_run_id(self, run_id: str):
        """Updates the current run ID."""
        self.run_id = run_id

    def trigger(self, skill_name: str) -> int:
        """Triggers a registered skill or procedure."""
        request = state_pb2.ReflexRequest(skill_name=skill_name)
        response = self.client.Trigger(request, metadata=self.metadata)
        return response.result

    def define_concept(self, name: str, schema: Dict[str, Any]) -> bool:
        """Define a concept with JSON schema."""
        request = state_pb2.DefineConceptRequest(
            run_id=self.run_id, name=name, schema_json=json.dumps(schema)
        )
        response = self.client.DefineConcept(request, metadata=self.metadata)
        return response.success

    def list_concepts(self) -> List[Dict[str, Any]]:
        """List all defined concepts."""
        request = state_pb2.ListConceptsRequest(run_id=self.run_id)
        response = self.client.ListConcepts(request, metadata=self.metadata)
        return [
            {"name": c.name, "schema": json.loads(c.schema_json)}
            for c in response.concepts
        ]

    def add_goal(
        self,
        description: str,
        priority: str = "medium",
        parent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a new goal to the agent's goal stack."""
        request = state_pb2.AddGoalRequest(
            run_id=self.run_id,
            description=description,
            priority=priority,
            parent_id=parent_id or "",
        )
        response = self.client.AddGoal(request, metadata=self.metadata)
        return {
            "id": response.id,
            "description": response.description,
            "priority": response.priority,
            "status": response.status,
            "parent_id": response.parent_id,
            "created_at": response.created_at,
        }

    def update_goal(self, goal_id: str, status: str) -> bool:
        """Update the status of an existing goal."""
        request = state_pb2.UpdateGoalRequest(
            run_id=self.run_id, goal_id=goal_id, status=status
        )
        response = self.client.UpdateGoal(request, metadata=self.metadata)
        return response.success

    def list_goals(self, status_filter: str = "") -> List[Dict[str, Any]]:
        """List all goals, optionally filtered by status."""
        request = state_pb2.ListGoalsRequest(
            run_id=self.run_id, status_filter=status_filter
        )
        response = self.client.ListGoals(request, metadata=self.metadata)
        return [
            {
                "id": g.id,
                "description": g.description,
                "priority": g.priority,
                "status": g.status,
                "parent_id": g.parent_id,
                "created_at": g.created_at,
            }
            for g in response.goals
        ]

    def submit_action(
        self, agent_id: str, action_type: str, details: Any
    ) -> Dict[str, Any]:
        """Submit an action for execution and logging."""
        request = state_pb2.ActionRequest(
            run_id=self.run_id,
            agent_id=agent_id,
            action_type=action_type,
            action_json=json.dumps(details),
        )
        response = self.client.SubmitAction(request, metadata=self.metadata)
        return {
            "action_id": response.action_id,
            "success": response.success,
            "result": json.loads(response.result_json)
            if response.result_json
            else None,
            "error": response.error,
            "duration_ms": response.duration_ms,
        }

    def get_action_log(
        self, limit: int = 100, action_type_filter: str = ""
    ) -> List[Dict[str, Any]]:
        """Get the action log for the current run."""
        request = state_pb2.ActionLogRequest(
            run_id=self.run_id, limit=limit, action_type_filter=action_type_filter
        )
        response = self.client.GetActionLog(request, metadata=self.metadata)
        return [
            {
                "action_id": e.action_id,
                "action_type": e.action_type,
                "action": json.loads(e.action_json) if e.action_json else None,
                "success": e.success,
                "result": json.loads(e.result_json) if e.result_json else None,
                "cycle_number": e.cycle_number,
                "timestamp": e.timestamp,
            }
            for e in response.entries
        ]

    def run_cycle(
        self, agent_id: str, candidates: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Run a decision cycle with action candidates."""
        proto_candidates = []
        if candidates:
            for c in candidates:
                proto_candidates.append(
                    state_pb2.ActionCandidate(
                        action_type=c.get("actionType", ""),
                        action_json=json.dumps(c.get("action", {})),
                        score=c.get("score", 0.0),
                        rationale=c.get("rationale", ""),
                    )
                )

        request = state_pb2.RunCycleRequest(
            run_id=self.run_id, agent_id=agent_id, candidates=proto_candidates
        )
        response = self.client.RunCycle(request, metadata=self.metadata)

        selected_action = response.selected_action
        action_result = response.action_result

        return {
            "cycle_number": response.cycle_number,
            "selected_action": {
                "actionType": selected_action.action_type,
                "action": json.loads(selected_action.action_json)
                if selected_action.action_json
                else None,
                "score": selected_action.score,
                "rationale": selected_action.rationale,
            }
            if selected_action.action_type
            else None,
            "action_result": {
                "action_id": action_result.action_id,
                "success": action_result.success,
                "result": json.loads(action_result.result_json)
                if action_result.result_json
                else None,
                "error": action_result.error,
            }
            if action_result.action_id
            else None,
            "planning_time_ms": response.planning_time_ms,
            "execution_time_ms": response.execution_time_ms,
            "timestamp": response.timestamp,
        }

    def get_cycle_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get history of decision cycles."""
        request = state_pb2.CycleHistoryRequest(run_id=self.run_id, limit=limit)
        response = self.client.GetCycleHistory(request, metadata=self.metadata)
        # Simplify response mapping for brevity, similar to run_cycle return
        # In a real replica, we would map all fields.
        return [{"cycle_number": c.cycle_number} for c in response.cycles]

    def delete_run(self) -> bool:
        """Deletes the current run session."""
        request = state_pb2.RunRequest(run_id=self.run_id)
        response = self.client.DeleteRun(request, metadata=self.metadata)
        return response.success
