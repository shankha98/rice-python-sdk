import os
import sys
import time
import asyncio
from dotenv import load_dotenv

# Add parent directory to path to import rice_sdk
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rice_sdk import Client

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


async def main():
    client = Client()
    try:
        print("Connecting to Storage...")
        client.connect()
        print("Connected!")

        # Check health
        health = client.storage.health()
        print("Health:", health)

        # Insert
        print("Inserting document...")
        node_id = int(time.time() * 1000)  # Must be Long/number for RiceDB
        insert_result = client.storage.insert(
            node_id, "Hello from Storage App", {"type": "example"}
        )
        print("Insert Result:", insert_result)

        # Search
        print("Searching...")
        search_results = client.storage.search("Hello", user_id=1)
        print("Search Results:", search_results)

        # Attempt state access (should fail if not enabled, but here config likely enables it)
        # The node example expects failure if state disabled.
        # Here we assume standard config which usually enables both.
        try:
            print("Checking State access...")
            _ = client.state
            print("State is enabled.")
        except Exception as e:
            print("State access prevented:", e)

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())
