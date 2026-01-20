import os
import sys
import asyncio
from rice_sdk import Client

# Add parent directory to path to import rice_sdk if not installed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    print("Initializing Rice Client...")
    # Assumes .env is in the current directory or configured
    client = Client()
    try:
        client.connect()
        print("Connected successfully.")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # --- Storage Example ---
    if client._config.storage.enabled:
        print("\n--- Storage ---")
        try:
            # Insert
            print("Inserting node...")
            res = client.storage.insert(
                node_id=1,
                text="Hello RiceDB from Python!",
                metadata={"source": "python-example"},
            )
            print(f"Insert result: {res}")

            # Search
            print("Searching...")
            results = client.storage.search("Hello")
            print(f"Found {len(results)} results:")
            for r in results:
                print(f"- [{r['id']}] {r['data']}")
        except Exception as e:
            print(f"Storage error: {e}")

    # --- State Example ---
    if client._config.state.enabled:
        print("\n--- State ---")
        try:
            # Focus
            print("Focusing on task...")
            client.state.focus("Demonstrating Python SDK")

            # Commit
            print("Committing memory...")
            client.state.commit(
                input_text="User ran the python example",
                output="Example ran successfully",
                action="run_example",
            )

            # Recall
            print("Recalling memory...")
            memories = client.state.reminisce("python example")
            print(f"Recalled {len(memories)} memories.")
            for m in memories:
                print(f"- {m.input} -> {m.outcome}")

        except Exception as e:
            print(f"State error: {e}")


if __name__ == "__main__":
    main()
