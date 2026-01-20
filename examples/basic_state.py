import os
import sys
import time
import asyncio
from dotenv import load_dotenv

# Add parent directory to path to import rice_sdk
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rice_sdk import Client

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


async def main():
    print("Testing Remote State Connection...")
    print("URL:", os.environ.get("STATE_INSTANCE_URL"))

    timestamp = int(time.time() * 1000)
    run_id = f"test-run-{timestamp}"
    input_text = f"Remote input {timestamp}"
    output_text = f"Remote output {timestamp}"

    print(f"Using Run ID: {run_id}")
    print(f"Using Input: {input_text}")

    # We assume configuration via environment variables or default rice.config.json
    client = Client(run_id=run_id)

    try:
        client.connect()
        print("Connected!")

        # =========================================================================
        # Core Memory Operations
        # =========================================================================
        print("\n=== Core Memory Operations ===")

        print("Focusing...")
        client.state.focus(f"Remote test focus {timestamp}")
        print("Focus successful.")

        print("Committing...")
        client.state.commit(input_text, output_text, action="test_reasoning")
        print("Commit successful.")

        print("Waiting 3s for indexing...")
        await asyncio.sleep(3)

        print("Reminiscing...")
        memories = client.state.reminisce(input_text)
        print(f"Found {len(memories)} memories.")
        print("Memories:", memories)

        if len(memories) > 0 and memories[0].input == input_text:
            print("VERIFICATION PASSED: Retrieved newly inserted memory.")
        else:
            # Note: reminisce returns Trace objects, ensure we check attributes correctly
            # Trace object has 'input' attribute.
            if (
                len(memories) > 0
                and hasattr(memories[0], "input")
                and memories[0].input == input_text
            ):
                print("VERIFICATION PASSED: Retrieved newly inserted memory.")
            else:
                print("VERIFICATION FAILED: Could not retrieve newly inserted memory.")

        # =========================================================================
        # Working Memory (Structured Variables)
        # =========================================================================
        print("\n=== Working Memory (Structured Variables) ===")

        # Set variables
        print("Setting variables...")
        client.state.set_variable("user_name", "Alice", "explicit")
        client.state.set_variable(
            "session_context",
            {
                "task": "code review",
                "language": "Python",
                "priority": "high",
            },
            "system",
        )
        client.state.set_variable("counter", 42, "reasoning")
        print("Variables set.")

        # Get a variable
        print("Getting variable 'user_name'...")
        user_name = client.state.get_variable("user_name")
        print("Variable:", user_name)

        # List all variables
        print("Listing all variables...")
        variables = client.state.list_variables()
        print("Variables:", variables)

        # Delete a variable
        print("Deleting variable 'counter'...")
        client.state.delete_variable("counter")
        print("Variable deleted.")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())
