import os
import sys
import time
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rice_sdk import Client

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


async def main():
    timestamp = int(time.time() * 1000)
    run_id = f"state-app-run-{timestamp}"
    input_text = f"StateApp unique input {timestamp}"
    output_text = f"StateApp unique output {timestamp}"

    print(f"Run ID: {run_id}")

    client = Client(run_id=run_id)

    try:
        print("Connecting to State...")
        client.connect()

        # =========================================================================
        # SECTION 1: Core Memory Operations
        # =========================================================================
        print("\n" + "=" * 60)
        print("SECTION 1: Core Memory Operations")
        print("=" * 60)

        # 1. Focus
        print("\n[1.1] Focusing...")
        focus_id = client.state.focus(f"Focus {timestamp}")
        print("Focus ID:", focus_id)

        # 2. Drift
        print("\n[1.2] Drifting...")
        drift_items = client.state.drift()
        print(f"Drift items: {len(drift_items)}")
        for item in drift_items:
            print(f" - {item.content}")

        # 3. Commit
        print("\n[1.3] Committing...")
        success = client.state.commit(
            input_text, output_text, action="test_action", agent_id="state-app-agent"
        )
        print("Commit success:", success)

        # 4. Reminisce
        print("\n[1.4] Reminiscing...")
        print("Waiting 6s for indexing...")
        await asyncio.sleep(6)

        memories = client.state.reminisce(input_text)
        print(f"Memories found: {len(memories)}")
        for m in memories:
            print(f" - {m.input} -> {m.outcome}")

        if len(memories) > 0 and memories[0].input == input_text:
            print("✓ VERIFICATION PASSED: Retrieved newly inserted memory.")
        else:
            print("✗ VERIFICATION FAILED: Could not retrieve newly inserted memory.")

        # =========================================================================
        # SECTION 2: Working Memory (Structured Variables)
        # =========================================================================
        print("\n" + "=" * 60)
        print("SECTION 2: Working Memory (Structured Variables)")
        print("=" * 60)

        # 2.1 Set Variables
        print("\n[2.1] Setting variables...")
        client.state.set_variable("current_task", "data_analysis", "system")
        client.state.set_variable(
            "user_preferences",
            {
                "theme": "dark",
                "language": "en",
                "notifications": True,
            },
            "explicit",
        )
        client.state.set_variable("iteration_count", 0, "reasoning")
        print("Variables set successfully.")

        # 2.2 Get Variable
        print("\n[2.2] Getting variable...")
        task_var = client.state.get_variable("current_task")
        print("current_task:", task_var)

        prefs_var = client.state.get_variable("user_preferences")
        print("user_preferences:", prefs_var)

        # 2.3 List Variables
        print("\n[2.3] Listing all variables...")
        all_vars = client.state.list_variables()
        print("Variables:", all_vars)

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())
