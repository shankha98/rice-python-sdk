from typing import Any, Dict
from ..state.client import StateClient


async def execute(name: str, args: Dict[str, Any], state_client: StateClient) -> Any:
    """
    Executes a tool call against the StateClient.
    Supports both sync and async execution (though python gRPC is mostly sync unless using AsyncChannel).
    Here we wrap the sync calls.
    """
    if name == "focus":
        return state_client.focus(args["content"])
    elif name == "recall":
        return state_client.reminisce(args["query"])
    elif name == "remember":
        if "content" in args:
            return state_client.commit(
                args["content"], "Stored in long-term memory", action="remember"
            )
        return state_client.commit(
            args.get("input", ""),
            args.get("outcome", ""),
            action=args.get("action", ""),
        )
    elif name == "setVariable":
        return state_client.set_variable(
            args["name"], args["value"], args.get("source", "explicit")
        )
    elif name == "getVariable":
        return state_client.get_variable(args["name"])
    elif name == "listVariables":
        return state_client.list_variables()
    elif name == "deleteVariable":
        return state_client.delete_variable(args["name"])
    elif name == "drift":
        return state_client.drift()
    elif name == "trigger":
        return state_client.trigger(args["skillName"])

    # Concepts
    elif name == "defineConcept":
        return state_client.define_concept(args["name"], args["schema"])
    elif name == "listConcepts":
        return state_client.list_concepts()

    # Goals
    elif name == "addGoal":
        return state_client.add_goal(
            args["description"], args.get("priority", "medium"), args.get("parentId")
        )
    elif name == "updateGoal":
        return state_client.update_goal(args["goalId"], args["status"])
    elif name == "listGoals":
        return state_client.list_goals(args.get("statusFilter", ""))

    # Actions
    elif name == "submitAction":
        return state_client.submit_action(
            args["agentId"], args["actionType"], args["actionDetails"]
        )
    elif name == "getActionLog":
        return state_client.get_action_log(
            args.get("limit", 100), args.get("actionTypeFilter", "")
        )

    # Decision Cycles
    elif name == "runCycle":
        return state_client.run_cycle(args["agentId"], args.get("candidates"))
    elif name == "getCycleHistory":
        return state_client.get_cycle_history(args.get("limit", 10))

    raise ValueError(f"Unknown tool: {name}")
