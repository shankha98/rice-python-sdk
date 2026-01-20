import os
import sys
import time
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rice_sdk import Client
from rice_sdk.tools.anthropic import state as anthropic_tools
from rice_sdk.tools.execute import execute

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


async def main():
    timestamp = int(time.time() * 1000)
    run_id = f"my-agent-run-{timestamp}"
    print(f"Run ID: {run_id}")

    client = Client(run_id=run_id)

    try:
        print("Connecting to Rice...")
        client.connect()
        print("Connected.")

        # Simulate LLM deciding to use 'remember' tool
        tool_call = {
            "name": "remember",
            "args": {"content": "User likes coffee"},
        }

        print(f"[LLM] Calling tool: {tool_call['name']} with", tool_call["args"])

        # Verify definitions are loaded
        print(f"[Demo] Loaded {len(anthropic_tools)} Anthropic tool definitions.")

        # Execute tool
        result = await execute(tool_call["name"], tool_call["args"], client.state)
        print(f"[Tool] Result: {result}")

        # Recall
        tool_call2 = {
            "name": "recall",
            "args": {"query": "coffee"},
        }
        print(f"[LLM] Calling tool: {tool_call2['name']} with", tool_call2["args"])

        result2 = await execute(tool_call2["name"], tool_call2["args"], client.state)
        print("[Tool] Result (Memories):")
        if isinstance(result2, list):
            for m in result2:
                # m is Trace object
                print(f" - {m.input if hasattr(m, 'input') else m}")
        else:
            print(result2)

    except Exception as e:
        print("Agent Error:", e)


if __name__ == "__main__":
    asyncio.run(main())
