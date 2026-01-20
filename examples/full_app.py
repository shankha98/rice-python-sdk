import os
import sys
import asyncio
from dotenv import load_dotenv

# Add parent directory to path to import rice_sdk
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rice_sdk import Client

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


async def main():
    client = Client()
    try:
        print("Connecting to All...")
        client.connect()

        print("Checking State...")
        # State focus returns focusId
        focus_id = client.state.focus("Full App Test")
        print("Focus ID:", focus_id)

        print("Checking Storage...")
        health = client.storage.health()
        print("Storage Health:", health)
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())
