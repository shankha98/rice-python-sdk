import os
import sys
import asyncio
from dotenv import load_dotenv

# Add parent directory to path to import rice_sdk
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rice_sdk import RiceDBClient

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


async def main():
    url = os.environ.get("STORAGE_INSTANCE_URL") or "localhost:50051"
    parts = url.split(":")
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 50051

    http_port = int(os.environ.get("STORAGE_HTTP_PORT", "3000"))
    token = os.environ.get("STORAGE_AUTH_TOKEN")

    print(f"Connecting to Storage at {host}:{port}")

    db = RiceDBClient(host, "auto", port, http_port, token)

    try:
        db.connect()
        print("Storage connected successfully")

        health = db.health()
        print("Health:", health)

        db.disconnect()
    except Exception as e:
        print("Storage connection failed:", e)


if __name__ == "__main__":
    asyncio.run(main())
