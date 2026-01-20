import os
import sys
import time
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rice_sdk import Client
from rice_sdk.tools.execute import execute

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


async def main():
    timestamp = int(time.time() * 1000)
    run_id = f"tool-test-run-{timestamp}"
    print(f"Run ID: {run_id}")

    client = Client(run_id=run_id)
    client.connect()

    content = f"Tool Test Content {run_id}"

    # =========================================================================
    # SECTION 1: Core Memory Tools
    # =========================================================================
    print("\n" + "=" * 60)
    print("SECTION 1: Core Memory Tools")
    print("=" * 60)

    # 1. Focus
    print("\n[1.1] Executing focus...")
    result_focus = await execute("focus", {"content": content}, client.state)
    print("Focus result:", result_focus)

    # Check Drift
    drift_items = client.state.drift()
    print("Drift items:", [i.content for i in drift_items])

    # 2. Remember
    print("\n[1.2] Executing remember...")
    rem_result = await execute(
        "remember",
        {
            "input": f"User input: {content}",
            "outcome": "System outcome",
            "action": "test",
        },
        client.state,
    )
    print("Remember result:", rem_result)

    # Wait
    print("Waiting 3s for indexing...")
    await asyncio.sleep(3)

    # 3. Recall
    print("\n[1.3] Executing recall...")
    memories = await execute(
        "recall",
        {"query": f"User input: {content}"},
        client.state,
    )

    # In python sdk reminisce returns list of Trace objects
    print(f"Recall found {len(memories)} items.")
    for m in memories:
        print(f" - {m.input} -> {m.outcome}")

    if len(memories) > 0 and memories[0].input == f"User input: {content}":
        print("✓ VERIFICATION PASSED: Retrieved newly inserted memory.")
    else:
        # Check if content was mapped to input
        if len(memories) > 0 and memories[0].input == f"User input: {content}":
            print("✓ VERIFICATION PASSED: Retrieved newly inserted memory.")
        else:
            print("✗ VERIFICATION FAILED: Could not retrieve newly inserted memory.")

    # =========================================================================
    # SECTION 2: Working Memory Tools
    # =========================================================================
    print("\n" + "=" * 60)
    print("SECTION 2: Working Memory Tools")
    print("=" * 60)

    # 2.1 setVariable
    print("\n[2.1] Executing setVariable...")
    await execute(
        "setVariable",
        {
            "name": "agent_state",
            "value": {"status": "active", "mode": "exploration"},
            "source": "system",
        },
        client.state,
    )
    print("Variable 'agent_state' set.")


if __name__ == "__main__":
    asyncio.run(main())
