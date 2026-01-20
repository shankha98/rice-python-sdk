# Rice Python SDK

Python SDK for Rice

## Installation

```bash
pip install rice-sdk
```

## Quick Start

The SDK provides a unified `Client` to access both Storage and State services.

```python
import asyncio
from rice_sdk import Client

# Initialize client (loads config from rice.config.json and .env)
client = Client()
client.connect()

# --- Storage ---
# Insert data
client.storage.insert(
  "unique-node-id", # Note: Should be numeric if using default GRPC types, or mapped properly
  "This is a piece of information stored in Rice Storage.",
  {"category": "example", "value": 123},
)

# Search for similar data
results = client.storage.search("information stored", k=5)
print(results)

# --- State (AI Agent Memory) ---
# Focus on a context/task
client.state.focus("User is asking about weather")

# Store a long-term memory (commit)
client.state.commit(
  "The user prefers metric units for temperature.",
  "User preference noted.",
  action="ground"
)

# Recall relevant memories
memories = client.state.reminisce("weather preferences")
print(memories)
```

## Configuration

The SDK loads configuration from `rice.config.json`, environment variables, and constructor options.

### 1. Configuration File (`rice.config.json`)

Control which services are enabled.

```json
{
  "storage": {
    "enabled": true
  },
  "state": {
    "enabled": true
  }
}
```

### 2. Environment Variables (`.env`)

Configure connection details and authentication.

```bash
# --- Storage ---
# URL of your Storage instance (default: localhost:50051)
STORAGE_INSTANCE_URL=localhost:50051
# Auth token (if enabled on server)
STORAGE_AUTH_TOKEN=my-secret-token
# User for auto-login (default: admin)
STORAGE_USER=admin

# --- State (AI Agent Memory) ---
# URL of your State instance
STATE_INSTANCE_URL=localhost:50051
# Auth token
STATE_AUTH_TOKEN=my-secret-token
# Default Run ID for memory sessions (optional)
STATE_RUN_ID=default-run-id
```

## State Features

The State service provides comprehensive AI agent memory and cognition capabilities.

### Core Memory Operations

```python
# Focus - Store in short-term working memory (Flux)
client.state.focus("Current task context")

# Drift - Read current working memory items
drift_items = client.state.drift()

# Commit - Store in long-term episodic memory (Echoes)
client.state.commit("User asked about weather", "Provided forecast", action="weather_lookup", agent_id="assistant")

# Reminisce - Recall relevant memories
memories = client.state.reminisce("weather questions", limit=5)
```

### Working Memory (Structured Variables)

Store and manage structured state for your agent's reasoning process.

```python
# Set a variable (supports any JSON-serializable value)
client.state.set_variable("user_name", "Alice", "explicit")
client.state.set_variable(
  "session_context",
  {
    "task": "code review",
    "language": "Python",
  },
  "system",
)

# Get a variable
user_var = client.state.get_variable("user_name")
print(user_var["value"]) # "Alice"

# List all variables
all_vars = client.state.list_variables()

# Delete a variable
client.state.delete_variable("user_name")
```

### Goals

Manage hierarchical goals for goal-directed agent behavior.

```python
# Add a goal
main_goal = client.state.add_goal("Complete project", "high")

# Add a sub-goal (with parent)
sub_goal = client.state.add_goal(
  "Review authentication module",
  "medium",
  parent_id=main_goal["id"]
)

# List goals (optionally filter by status)
all_goals = client.state.list_goals()
active_goals = client.state.list_goals(status_filter="active")

# Update goal status
client.state.update_goal(sub_goal["id"], "achieved")
```

### Actions

Log and track agent actions for auditing and learning.

```python
# Submit an action
result = client.state.submit_action("agent-1", "reason", {
  "thought": "Analyzing the code structure",
  "conclusion": "Start with main entry point",
})

# Get action log
action_log = client.state.get_action_log(limit=100)
```

### Decision Cycles

Run autonomous decision cycles with scored action candidates.

```python
# Run a decision cycle with candidates
cycle_result = client.state.run_cycle("agent-1", [
  {
    "actionType": "reason",
    "action": { "thought": "Should analyze data first" },
    "score": 0.8,
    "rationale": "Data analysis is foundational",
  },
  {
    "actionType": "retrieve",
    "action": { "query": "relevant documentation" },
    "score": 0.6,
    "rationale": "Documentation might help",
  },
])

print(cycle_result["selected_action"])
```

## AI Tool Definitions

The SDK provides pre-built tool definitions tailored for popular LLM providers.

### OpenAI Example

```python
from rice_sdk.tools.openai import state as openai_tools
from rice_sdk.tools.execute import execute
from rice_sdk import Client

client = Client()
client.connect()

# 1. Pass tools to OpenAI
# response = openai.chat.completions.create(..., tools=openai_tools)

# 2. Execute tools
# For each tool call:
# result = execute(tool_call.function.name, json.loads(tool_call.function.arguments), client.state)
```
